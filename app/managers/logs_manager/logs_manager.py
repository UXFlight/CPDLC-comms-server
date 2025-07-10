
from app.classes.log_entry.log_entry import LogEntry
from app.constants.logs_array import default_logs
from enum import Enum

class DatalinkStatus(Enum):
    NEW = "new"
    PENDING = "pending"
    REQUESTED = "requested"
    CLOSED = "closed"
    REJECTED = "rejected"
    OPENED = "opened"
    ACK = "ack"
    INFO = "info"
    EXPIRED = "expired"


class LogsManager:
    def __init__(self, mongodb):
        self.logs = [
            LogEntry(
                ref="UM74",
                content="PROCEED DIRECT TO OAKLE",
                direction="uplink",
                status="NEW",
                urgency="Normal",
                intent="Instruction to proceed directly from its present position to the specified position.",
                mongodb=mongodb
            )
        ]
        self.mongodb = mongodb

    def get_logs(self):
        return [log.to_dict() for log in self.logs]
    
    def get_log_by_id(self, log_id):
        for log in self.logs:
            if log.id == log_id:
                return log
        return None

    def to_dict(self):
        return self.get_logs()
    
    def filter_by_timestamp(self):
        return sorted(self.logs, key=lambda log: log.timestamp, reverse=True)

    def add_log(self, entry):
        message = self.mongodb.find_datalink_by_ref(entry.get("messageRef"))
        type = "downlink" if "DM" in message.get("Ref_Num") else "uplink"
        
        new_log = LogEntry(
            ref=message.get("Ref_Num"),
            content=entry.get("formattedMessage"),
            direction=type,
            status=self.set_new_log_status(message).value,
            intent=message.get("Message_Intent"),
            additional=entry.get("additional"), 
            urgency=entry.get("urgency"),
            mongodb=self.mongodb,
        )
        self.logs.append(new_log)
        return new_log
    
    def set_new_log_status(self, datalink):
        if "U" in datalink.get("Ref_Num", " "):
            return DatalinkStatus.NEW if LogEntry.is_response_required(datalink) else DatalinkStatus.OPENED
        else:
            return DatalinkStatus.REQUESTED if LogEntry.is_response_required(datalink) else DatalinkStatus.OPENED

