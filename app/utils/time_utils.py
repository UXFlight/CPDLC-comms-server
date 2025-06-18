from datetime import datetime
from zoneinfo import ZoneInfo

def get_current_timestamp():
    now = datetime.now(ZoneInfo("America/Toronto"))
    return now.strftime("%H:%M:%S")
