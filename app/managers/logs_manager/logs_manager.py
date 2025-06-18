
from app.classes.log_entry.log_entry import LogEntry
from app.database.log_storage import load_logs, save_logs
from app.utils.time_utils import get_current_timestamp
from app.constants.logs_array import default_logs


class LogsManager:
    def __init__(self):
        self.logs = default_logs

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
        d_message = LogEntry.find_DM_by_ref(entry.get("messageRef"))
        u_message = None

        if not d_message:
            u_message = LogEntry.find_UM_by_ref(entry.get("messageRef"))

        new_log = LogEntry(
            ref=d_message.get("Ref_Num") if d_message else u_message.get("Ref_Num"),
            content=entry.get("formattedMessage"),
            direction="downlink" if d_message else "uplink",
            status="opened" if d_message else "new",
            intent=d_message.get("Message_Intent") if d_message else u_message.get ("Message_Intent"),
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
