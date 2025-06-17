import datetime
from time import timezone


def get_current_timestamp():
    return datetime.now(timezone.utc).isoformat()