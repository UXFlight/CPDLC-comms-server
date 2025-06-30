from datetime import datetime
from app.classes.log_entry.log_entry import LogEntry
from app.utils.time_utils import get_current_timestamp

default_logs = [
    LogEntry(
        ref="UM74",
        content="PROCEED DIRECT TO OAKLE",
        direction="uplink",
        status="NEW",
        intent="Instruction to proceed directly from its present position to the specified position."
    )
]
