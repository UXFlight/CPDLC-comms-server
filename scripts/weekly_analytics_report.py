#!/usr/bin/env python3
import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from app.classes.logging import log_error
from app.services.weekly_report_service import generate_and_send_weekly_report


def main() -> int:
    try:
        ok = generate_and_send_weekly_report()
        return 0 if ok else 1
    except Exception as e:
        log_error(None, "analytics_report_failed", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
