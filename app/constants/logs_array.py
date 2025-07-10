from app.classes.log_entry.log_entry import LogEntry
from app.database.mongo_db import MongoDb

default_logs = [
    LogEntry(
        ref="UM74",
        content="PROCEED DIRECT TO OAKLE",
        direction="uplink",
        status="NEW",
        urgency="Normal",
        intent="Instruction to proceed directly from its present position to the specified position.",
        mongodb=MongoDb()
    )
]
