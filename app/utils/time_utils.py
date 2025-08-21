from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def get_current_timestamp():
    now = datetime.now(ZoneInfo("America/Toronto"))
    return now.strftime("%H:%M:%S")


def get_current_timestamp_pos_report():
    now = datetime.now(ZoneInfo("America/Toronto"))
    return int(now.timestamp()) 

def parse_duration_to_seconds(duration_str):
    h, m, s = map(int, duration_str.split(":"))
    return int(timedelta(hours=h, minutes=m, seconds=s).total_seconds())

def format_timestamp_utc(timestamp_sec):
    dt = datetime.fromtimestamp(timestamp_sec, ZoneInfo("UTC"))
    return dt.strftime("%H:%M:%S")
