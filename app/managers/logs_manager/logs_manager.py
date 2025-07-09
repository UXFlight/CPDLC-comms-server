
from app.classes.log_entry.log_entry import LogEntry
from app.database.log_storage.log_storage import load_logs, save_logs
from app.utils.time_utils import get_current_timestamp
from app.constants.logs_array import default_logs


class LogsManager:
    def __init__(self, mongodb):
        self.logs = default_logs
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
            status="pending" if type =="downlink" else "new",
            intent=message.get("Message_Intent"),
            additional=entry.get("additional"), 
            urgency=entry.get("urgency"),
            mongodb=self.mongodb,
        )
        self.logs.append(new_log)
        return new_log
    
    def change_status(self, log_id, new_status):
        log = self.get_log_by_id(log_id)
        if log:
            log.status = new_status
            return log
        return None

    # def filter_by(self, criteria):
    #     if criteria == "NEW"
