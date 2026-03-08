import json
import os
import threading
from urllib import request


def send_telegram_message(text: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()
    if not token or not channel_id or not text:
        return

    def _send() -> None:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = json.dumps({"chat_id": channel_id, "text": text}).encode("utf-8")
            req = request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with request.urlopen(req, timeout=2):
                pass
        except Exception:
            # Never break app flow on notifier failures.
            return

    threading.Thread(target=_send, daemon=True).start()
