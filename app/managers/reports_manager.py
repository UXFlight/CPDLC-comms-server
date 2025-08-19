from typing import Callable

from app.classes.fsm.fsm_scenarios.emergency_scenario import SCENARIO_EMERGENCY
from app.classes.report.adsc_contract import ADSCContract
from app.classes.report.emergency_report import EmergencyReport
from app.classes.report.position_report import PositionReport
from app.constants.RoutineSnapshot import RoutineSnapshot
from app.managers.adsc_manager import AdscManager

class ReportsManager:
    def __init__(self, socket, status, room, logs, scenario_manager, get_snapshot: Callable[[], RoutineSnapshot] = None):
        self.socket = socket
        self.status = status
        self.room = room
        self.logs = logs
        self.scenario_manager = scenario_manager    
        self._get_snapshot = get_snapshot

        self.position_reports: list[PositionReport] = []
        self.index_reports = []
        self.monitoring_reports = []
        self.adsc_manager = None
        self.emergency_report : EmergencyReport = None

    def set_snapshot_provider(self, fn: Callable[[], RoutineSnapshot]):
        self.adsc_manager = AdscManager(self.socket, self.status, self.room, self.logs, self.scenario_manager, fn)
        self._get_snapshot = fn

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
