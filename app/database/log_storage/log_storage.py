import json
from pathlib import Path

LOG_FILE_PATH = Path("log_storage/logs.json")

LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_logs():
    if LOG_FILE_PATH.exists():
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_logs(logs):
    with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, default=str)
