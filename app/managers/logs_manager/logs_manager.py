
from app.classes.fsm.fsm_types import Scenario
from app.classes.log_entry.log_entry import LogEntry
from app.constants.logs_array import default_logs
from enum import Enum

from app.constants.responses import REPORT_INITIATION

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
    def __init__(self, mongodb, socket, scenario_manager):
        self.logs = []
        self._mongodb = mongodb
        self.socket = socket
        self.scenario_manager = scenario_manager

    def get_logs(self):
        def get_comparison_timestamp(log):
            if log.communication_thread and len(log.communication_thread) > 0:
                return log.communication_thread[-1].timestamp
            return log.timestamp

        # Trier tous les logs selon le bon timestamp (du plus récent au plus ancien)
        sorted_logs = sorted(
            self.logs,
            key=get_comparison_timestamp,
            reverse=True
        )

        # Convertir les logs triés en dictionnaires
        logs_dict = [log.to_dict() for log in sorted_logs]

        return logs_dict
    
    def get_log_by_id(self, log_id):
        for log in self.logs:
            if log.id == log_id:
                return log
            else:
                for child in log.communication_thread:
                    if child.id == log_id:
                        return child
        return None

    def get_parent_by_child_id(self, child_id):
        for log in self.logs:
            if log.id == child_id:
                return log
            else:
                for child in log.communication_thread:
                    if child.id == child_id:
                        return log
        return None

    def to_dict(self):
        return self.get_logs()
    
    def filter_by_timestamp(self):
        return sorted(self.logs, key=lambda log: log.timestamp, reverse=True)

    def create_add_log(self, entry, scenario: Scenario = None):
        message = self._mongodb.find_datalink_by_ref(entry.get("messageRef"))
        type = "downlink" if "DM" in message.get("Ref_Num") else "uplink"

        new_log = LogEntry(
            ref=message.get("Ref_Num"),
            content=entry.get("formattedMessage"),
            direction=type,
            status=LogsManager.set_new_log_status(message).value,
            intent=message.get("Message_Intent"),
            additional=entry.get("additional", []), 
            urgency=entry.get("urgency", "normal"),
            mongodb=self._mongodb,
            response_required=LogEntry.is_response_required(message),
            acceptable_responses=message.get("Acceptable_responses", []),
            id=entry.get("id", None),
        )
        self.logs.append(new_log)
        if scenario:
            self.start_scenario(type, new_log.ref, new_log.content, scenario)
        return new_log

    @staticmethod
    def create_log(mongodb, log_ref: str, content: str):
        message = mongodb.find_datalink_by_ref(log_ref)
        type = "downlink" if "DM" in message.get("Ref_Num") else "uplink"

        new_log = LogEntry(
            ref=message.get("Ref_Num"),
            content=content,
            direction=type,
            status=LogsManager.set_new_log_status(message).value,
            intent=message.get("Message_Intent"),
            additional=[],
            urgency="normal",
            mongodb=mongodb,
            response_required=LogEntry.is_response_required(message),
            acceptable_responses=message.get("Acceptable_responses", []),
            id=None,
        )
        return new_log
    
    def remove_log_by_id(self, log_id):
        for i, log in enumerate(self.logs):
            if log.id == log_id:
                del self.logs[i]
                return True
        return False

    @staticmethod
    def set_new_log_status(datalink):
        if "U" in datalink.get("Ref_Num", " "):
            return DatalinkStatus.NEW if LogEntry.is_response_required(datalink) else DatalinkStatus.OPENED
        else:
            return DatalinkStatus.REQUESTED if LogEntry.is_response_required(datalink) else DatalinkStatus.OPENED

    def start_scenario(self, type, pilot_ref, pilot_text, scenario: Scenario):
        self.scenario_manager.set_scenario(scenario)
        if type == "downlink":
            self.scenario_manager.on_pilot_dm(pilot_ref, pilot_text)
        else: 
            self.scenario_manager.enter("atc_entry")

    def add_log(self, log: LogEntry, thread_id = None, scenario: Scenario = None):
        if thread_id:
            return self.handle_response(log, thread_id)
        self.logs.append(log)
        if scenario:
            self.start_scenario(type, log.ref, log.content, scenario)
        return log
            

    def handle_response(self, log: LogEntry, thread_id: str):
        parent = self.get_parent_by_child_id(thread_id)
        if parent:
            parent.communication_thread.append(log)
            return parent
        else:
            self.logs.append(log)
            return log

    def position_request_pending(self):
        for log in self.logs:
            if log.ref == "UM147" and not log.ended:
                print(f"Position request pending for log {log.id}")
                return log.id
        return None