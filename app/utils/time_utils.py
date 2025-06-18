from datetime import datetime, timezone

# def get_current_timestamp():
#     return datetime.now(timezone.utc).isoformat()

def get_current_timestamp():
    now = datetime.now(timezone.utc)
    hh_mm_ss = now.strftime("%H:%M:%S")
    return f"{hh_mm_ss}"