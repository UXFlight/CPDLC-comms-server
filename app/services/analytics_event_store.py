from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

EVENTS_FILE_PATH = (
    Path(__file__).resolve().parents[1] / "database" / "log_storage" / "analytics_events.jsonl"
)
MAX_FILE_BYTES = 3 * 1024 * 1024
RETENTION_DAYS = 14
MIN_LINES_TO_KEEP = 500

_LOCK = threading.Lock()


def _ensure_parent() -> None:
    EVENTS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _safe_json_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): _safe_json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_safe_json_value(v) for v in value]
    return str(value)


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _prune_if_needed() -> None:
    if not EVENTS_FILE_PATH.exists():
        return
    try:
        if EVENTS_FILE_PATH.stat().st_size <= MAX_FILE_BYTES:
            return
    except Exception:
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    kept_lines: list[str] = []

    try:
        with EVENTS_FILE_PATH.open("r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                keep = False
                try:
                    event = json.loads(line)
                    ts = _parse_timestamp(event.get("timestamp")) if isinstance(event, dict) else None
                    keep = bool(ts and ts >= cutoff)
                except Exception:
                    keep = False
                if keep:
                    kept_lines.append(line)

        if len(kept_lines) < MIN_LINES_TO_KEEP:
            with EVENTS_FILE_PATH.open("r", encoding="utf-8") as f:
                tail = [ln.strip() for ln in f if ln.strip()]
            kept_lines = tail[-MIN_LINES_TO_KEEP:]

        with EVENTS_FILE_PATH.open("w", encoding="utf-8") as f:
            for line in kept_lines:
                f.write(line + "\n")
    except Exception:
        return


def record_event(
    kind: str,
    client_id: str,
    event: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "client_id": client_id,
        "event": event,
        "metadata": _safe_json_value(metadata or {}),
    }

    line = json.dumps(payload, ensure_ascii=True)
    _ensure_parent()
    try:
        with _LOCK:
            _prune_if_needed()
            with EVENTS_FILE_PATH.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
    except Exception:
        return


def load_events() -> list[dict[str, Any]]:
    if not EVENTS_FILE_PATH.exists():
        return []

    events: list[dict[str, Any]] = []
    try:
        with EVENTS_FILE_PATH.open("r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                    if isinstance(parsed, dict):
                        events.append(parsed)
                except json.JSONDecodeError:
                    continue
    except Exception:
        return []
    return events
