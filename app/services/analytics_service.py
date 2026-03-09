from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Any

from app.constants.country_flags import COUNTRY_FLAGS, COUNTRY_NAMES, FALLBACK_FLAG
from app.services.analytics_event_store import load_events
from app.services.ip_country_service import detect_country_code

WEEK_HOURS = 7 * 24


@dataclass
class CountryMetric:
    code: str
    name: str
    flag: str
    users: int = 0
    events: int = 0


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


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _round(value: float) -> float:
    return round(value, 2)


class AnalyticsService:
    def __init__(self, now: datetime | None = None):
        self.now = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
        self.week_start = self.now - timedelta(days=7)

    def _weekly_events(self) -> list[dict[str, Any]]:
        weekly: list[dict[str, Any]] = []
        for event in load_events():
            ts = _parse_timestamp(event.get("timestamp"))
            if not ts:
                continue
            if self.week_start <= ts <= self.now:
                normalized = dict(event)
                normalized["_dt"] = ts
                normalized["metadata"] = (
                    event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
                )
                weekly.append(normalized)
        weekly.sort(key=lambda e: e["_dt"])
        return weekly

    def _session_metrics(self, events: list[dict[str, Any]]) -> tuple[int, int, float, float]:
        active = 0
        peak = 0
        durations: list[float] = []
        starts_by_client: dict[str, list[datetime]] = defaultdict(list)

        for event in events:
            if event.get("kind") != "user_action":
                continue
            name = event.get("event")
            client = str(event.get("client_id") or "-")
            if name == "session_create":
                active += 1
                peak = max(peak, active)
                starts_by_client[client].append(event["_dt"])
            elif name == "session_remove":
                if active > 0:
                    active -= 1
                if starts_by_client[client]:
                    started_at = starts_by_client[client].pop(0)
                    durations.append((event["_dt"] - started_at).total_seconds())

        avg_session_duration = mean(durations) if durations else 0.0
        return active, peak, _round(avg_session_duration), float(len(durations))

    def _country_metrics(self, events: list[dict[str, Any]]) -> list[CountryMetric]:
        cache: dict[str, str] = {}
        user_country: dict[str, str] = {}
        events_by_country: Counter[str] = Counter()
        users_by_country: Counter[str] = Counter()

        for event in events:
            metadata = event.get("metadata", {})
            client = str(event.get("client_id") or "-")
            ip = metadata.get("ip")
            country = None

            if ip:
                country = detect_country_code(str(ip), cache=cache)
                if client != "-":
                    user_country[client] = country
            elif client in user_country:
                country = user_country[client]

            if not country:
                continue
            events_by_country[country] += 1

        for country in user_country.values():
            users_by_country[country] += 1

        keys = set(events_by_country.keys()) | set(users_by_country.keys())
        metrics: list[CountryMetric] = []
        for code in keys:
            metrics.append(
                CountryMetric(
                    code=code,
                    name=COUNTRY_NAMES.get(code, code),
                    flag=COUNTRY_FLAGS.get(code, FALLBACK_FLAG),
                    users=users_by_country.get(code, 0),
                    events=events_by_country.get(code, 0),
                )
            )

        metrics.sort(key=lambda m: (m.users, m.events), reverse=True)
        return metrics

    def compute_weekly_stats(self) -> dict[str, Any]:
        events = self._weekly_events()
        total_events = len(events)
        errors = [e for e in events if e.get("kind") == "error"]
        user_actions = [e for e in events if e.get("kind") == "user_action"]

        unique_users = {
            str(e.get("client_id"))
            for e in user_actions
            if str(e.get("client_id") or "-") != "-"
        }

        routes_started = sum(1 for e in user_actions if e.get("event") == "route_started")
        routes_completed = sum(1 for e in user_actions if e.get("event") == "route_completed")
        route_completion_rate = (routes_completed / routes_started * 100) if routes_started else 0.0

        route_completion_values: list[float] = []
        for event in user_actions:
            if event.get("event") == "route_session_closed":
                value = _to_float(event.get("metadata", {}).get("route_completion_pct"))
                if value is not None:
                    route_completion_values.append(value)
        avg_route_completion_pct = mean(route_completion_values) if route_completion_values else 0.0

        error_rate = (len(errors) / total_events * 100) if total_events else 0.0
        avg_events_per_hour = total_events / WEEK_HOURS if total_events else 0.0

        cpdlc_events = sum(
            1
            for e in user_actions
            if any(
                token in str(e.get("event", ""))
                for token in ("message", "route", "routine", "authentication", "position", "adsc")
            )
        )
        failed_operations = len(errors) + sum(
            1 for e in user_actions if str(e.get("event", "")).endswith("_failed")
        )

        connect_count = Counter(
            str(e.get("client_id"))
            for e in user_actions
            if e.get("event") == "connect" and str(e.get("client_id") or "-") != "-"
        )
        reconnections = sum(max(count - 1, 0) for count in connect_count.values())

        active_sessions, peak_sessions, avg_session_duration_sec, completed_sessions = self._session_metrics(
            events
        )
        country_metrics = self._country_metrics(events)

        return {
            "window_start_utc": self.week_start.isoformat(),
            "window_end_utc": self.now.isoformat(),
            "users_this_week": len(unique_users),
            "active_sessions": active_sessions,
            "peak_active_sessions": peak_sessions,
            "routes_started": routes_started,
            "routes_completed": routes_completed,
            "route_completion_rate": _round(route_completion_rate),
            "average_route_completion_pct": _round(avg_route_completion_pct),
            "events_processed": total_events,
            "errors": len(errors),
            "error_rate": _round(error_rate),
            "average_events_per_hour": _round(avg_events_per_hour),
            "cpdlc_events": cpdlc_events,
            "failed_operations": failed_operations,
            "reconnections": reconnections,
            "average_session_duration_sec": _round(avg_session_duration_sec),
            "completed_sessions": int(completed_sessions),
            "top_countries": [
                {
                    "code": metric.code,
                    "name": metric.name,
                    "flag": metric.flag,
                    "users": metric.users,
                    "events": metric.events,
                }
                for metric in country_metrics[:5]
            ],
        }
