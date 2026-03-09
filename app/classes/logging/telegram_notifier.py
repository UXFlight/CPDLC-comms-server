import json
import os
import threading
from urllib import request
from urllib.error import HTTPError, URLError


def _telegram_config() -> tuple[str, str]:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()
    return token, channel_id


def _post_telegram_message(text: str) -> tuple[bool, str | None]:
    token, channel_id = _telegram_config()
    if not token or not channel_id or not text:
        return False, "telegram_not_configured"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": channel_id, "text": text}).encode("utf-8")
    req = request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=6) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
        if resp.status != 200:
            return False, f"http_status_{resp.status}"
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {}
        if isinstance(parsed, dict) and parsed.get("ok") is True:
            return True, None
        if isinstance(parsed, dict):
            return False, str(parsed.get("description") or "telegram_response_not_ok")
        return False, "telegram_response_not_ok"
    except HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="ignore")
            parsed = json.loads(body) if body else {}
            if isinstance(parsed, dict) and parsed.get("description"):
                return False, str(parsed["description"])
        except Exception:
            pass
        return False, f"http_error_{e.code}"
    except URLError:
        return False, "telegram_unreachable"
    except Exception:
        return False, "telegram_send_failed"


def send_telegram_message(text: str) -> None:
    token, channel_id = _telegram_config()
    if not token or not channel_id or not text:
        return

    def _send() -> None:
        _post_telegram_message(text)

    threading.Thread(target=_send, daemon=True).start()


def send_telegram_message_sync(text: str) -> tuple[bool, str | None]:
    return _post_telegram_message(text)
