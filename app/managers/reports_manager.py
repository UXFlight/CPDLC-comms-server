import re
from typing import Callable

from app.classes.fsm.fsm_scenarios.emergency_scenario import SCENARIO_EMERGENCY
from app.classes.report.adsc_contract import ADSCContract
from app.classes.report.emergency_report import EmergencyReport
from app.classes.report.index_report import IndexReport
from app.classes.report.monitoring_report import MonitoringReport
from app.classes.report.position_report import PositionReport
from app.constants.RoutineSnapshot import RoutineSnapshot
from app.managers.adsc_manager import AdscManager

INDEX_RESPONSES = {
    "UM130": "DM31",
    "UM180": "DM76",
}


class ReportsManager:
    def __init__(self, mongodb, socket, status, room, logs, scenario_manager, get_snapshot: Callable[[], RoutineSnapshot] = None):
        self.mongodb = mongodb
        self.socket = socket
        self.status = status
        self.room = room
        self.logs = logs
        self.scenario_manager = scenario_manager
        self._get_snapshot = get_snapshot

        self.position_reports: list[PositionReport] = []
        self.index_reports = []
        self.monitoring_report : MonitoringReport = None
        self.adsc_manager = None
        self.emergency_report : EmergencyReport = None

    def set_snapshot_provider(self, fn: Callable[[], RoutineSnapshot]):
        self.adsc_manager = AdscManager(self.socket, self.status, self.room, self.logs, self.scenario_manager, fn)
        self._get_snapshot = fn

    # monitoring report 
    def set_monitoring_report(self, data: dict) -> MonitoringReport:
        report = MonitoringReport(
            facility=data.get("facility"),
            facility_designation=data.get("designation"),
            facility_name=data.get("name"),
            vhf=data.get("vhf"),
            ref=data.get("ref", "DM89")
        )
        self.monitoring_report = report
        report_dict = {
            "facility": report.facility,
            "designation": report.facility_designation,
            "name": report.facility_name,
            "vhf": report.vhf
        }
        self.socket.send("monitoring_report", report_dict, room=self.room)

    # position reports
    def add_position_report(self, report: PositionReport):
        self.position_reports.insert(0, report)
        self.socket.send("position_report", report)

    def set_emergency_report(self, report: EmergencyReport, thread_id :str):
        self.emergency_report = report
        emrg_ref = "DM55" if report.type == "PAN" else "DM56"

        self.scenario_manager.start_scenario(
            scenario=SCENARIO_EMERGENCY,
            room=self.room,
            initiator="PILOT",
            pilot_ref=emrg_ref,
            thread_id=thread_id
        )

    # index reports 
    def add_index_report(self, data):
        report = IndexReport(
            ref=data.get("ref"),
            id=data.get("id"),
            label=data.get("label"),
            status=data.get("status")
        )
        dl = self.mongodb.find_datalink_by_ref(report.ref)
        template = dl.get("Message_Element", "")
        value = self.extract_value_from_label(report.label, template)

        expected_dm = INDEX_RESPONSES.get(report.ref)  # ex: UM6 → DM31
        response_text = self.build_response_message(expected_dm, value)
        report.result = {
            "ref": expected_dm,
            "text": response_text
        }
        self.index_reports.append(report)

        self.socket.send("index_report_response", {"id": report.id, "result": report.result}, room=self.room)


    def extract_placeholder(self, text):
        match = re.search(r"\[(.*?)\]", text)
        return match.group(1) if match else None

    def extract_value_from_label(self, label, template):
        placeholder = self.extract_placeholder(template)
        if not placeholder:
            return None
        return label.replace(template.replace(f"[{placeholder}]", ""), "").strip()
    
    def build_response_message(self, dm_ref, value):
        dl = self.mongodb.find_datalink_by_ref(dm_ref)
        template = dl.get("Message_Element", "")
        placeholder = self.extract_placeholder(template)
        if not placeholder:
            return template  # rien à remplacer
        return template.replace(f"[{placeholder}]", value)