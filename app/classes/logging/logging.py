import logging
import os
from typing import Any
from .telegram_notifier import send_telegram_message
from app.services.analytics_event_store import record_event

USER_ACTION_LEVEL = 25
LOGGER_NAME = "cpdlc"
DEFAULT_CLIENT_ID = "-"

logging.addLevelName(USER_ACTION_LEVEL, "USER_ACTION")

_LOGGER: logging.Logger | None = None


class _ContextFormatter(logging.Formatter):
    default_time_format = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "client_id"):
            record.client_id = DEFAULT_CLIENT_ID
        if not hasattr(record, "event"):
            record.event = "-"
        if not hasattr(record, "meta"):
            record.meta = ""
        return super().format(record)


def _stringify(value: Any) -> str:
    text = str(value).replace("\n", " ").replace("|", "/").strip()
    return text or "-"


def _compact_client_id(client_id: str | None) -> str:
    if not client_id:
        return DEFAULT_CLIENT_ID
    return client_id[:7]


def _normalize_client_id(client_id: str | None) -> str:
    if not client_id:
        return DEFAULT_CLIENT_ID
    return str(client_id)


def _build_meta(fields: dict[str, Any]) -> str:
    if not fields:
        return ""
    chunks: list[str] = []
    for key, value in fields.items():
        if value is None:
            continue
        chunks.append(f" | {key}={_stringify(value)}")
    return "".join(chunks)


def get_logger() -> logging.Logger:
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    logger = logging.getLogger(LOGGER_NAME)
    logger.propagate = False

    level_name = os.getenv("APP_LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level_name, logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = _ContextFormatter(
            "%(asctime)s | %(levelname)s | client=%(client_id)s | event=%(event)s%(meta)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    suppress_third_party = os.getenv("SUPPRESS_THIRD_PARTY_LOGS", "true").lower() == "true"
    if suppress_third_party:
        logging.getLogger("werkzeug").setLevel(logging.WARNING)
        logging.getLogger("engineio").setLevel(logging.WARNING)
        logging.getLogger("socketio").setLevel(logging.WARNING)
        logging.getLogger("eventlet.wsgi").setLevel(logging.WARNING)

    _LOGGER = logger
    return logger


def log_user_action(
    client_id: str,
    event: str,
    user_agent: str | None = None,
    ip: str | None = None,
    **extra: Any,
) -> None:
    logger = get_logger()
    metadata: dict[str, Any] = {}
    if user_agent:
        metadata["agent"] = user_agent
    if ip:
        metadata["ip"] = ip
    metadata.update(extra)
    logger.log(
        USER_ACTION_LEVEL,
        "user_action",
        extra={
            "client_id": _compact_client_id(client_id),
            "event": event,
            "meta": _build_meta(metadata),
        },
    )
    try:
        record_event(
            kind="user_action",
            client_id=_normalize_client_id(client_id),
            event=event,
            metadata=metadata,
        )
    except Exception:
        return


def log_error(
    client_id: str | None,
    event: str,
    error: Exception | str,
    **extra: Any,
) -> None:
    logger = get_logger()
    metadata: dict[str, Any] = {"reason": _stringify(error)}
    if isinstance(error, Exception):
        metadata["error_type"] = type(error).__name__
    metadata.update(extra)
    extra_payload = {
        "client_id": _compact_client_id(client_id),
        "event": event,
        "meta": _build_meta(metadata),
    }
    record = logger.makeRecord(
        logger.name,
        logging.ERROR,
        fn="",
        lno=0,
        msg="error",
        args=(),
        exc_info=None,
        extra=extra_payload,
    )
    if logger.isEnabledFor(logging.ERROR):
        logger.handle(record)

    try:
        record_event(
            kind="error",
            client_id=_normalize_client_id(client_id),
            event=event,
            metadata=metadata,
        )
    except Exception:
        pass

    try:
        if logger.handlers and logger.handlers[0].formatter:
            log_message = logger.handlers[0].formatter.format(record)
            send_telegram_message(log_message)
    except Exception:
        return
