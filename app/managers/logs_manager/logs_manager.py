
from app.classes.log_entry.log_entry import LogEntry
from app.database.log_storage import load_logs, save_logs
from app.utils.time_utils import get_current_timestamp


class LogsManager:
    def __init__(self):
        self.logs = []

    def add_log(self, entry):
        self.logs.append(entry)

    def get_logs(self):
        logs = load_logs()  
        if not logs:
            print("No logs found, initializing with an empty list.")
            return []
        print(f"Loaded {len(logs)} logs from storage.")
        return logs

    def to_dict(self):
        return self.get_logs()
    
    def add_log(self, log):
        d_message = LogEntry.find_DM_by_ref(log.messageRef)
        if not d_message:
            u_message = LogEntry.find_UM_by_ref(log.messageRef)
        
        new_log = LogEntry(
            ref=(d_message.Ref_Num | u_message.Ref_Num),
            content=log.formattedMessage,
            direction="DOWNLINK" if d_message else "UPLINK",
            status="OPENED" if d_message else "NEW",
            timestamp=get_current_timestamp(),
            intent=d_message.Message_Intent if d_message else u_message.Message_Intent,
        )

        logs = load_logs()
        logs.append(new_log)
        save_logs(logs)

        return logs
    
    # def filter_by(self, criteria):
    #     if criteria == "NEW"
