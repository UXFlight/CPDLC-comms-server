# UM Categories
from app.classes.report.adsc_contract import ADSCContract
from app.classes.report.index_report import IndexReport
from app.classes.report.monitoring_report import MonitoringReport
from app.classes.report.position_report import PositionReport


ADSC_EMERGENCY = ["UM169ak"] #confirm adsc emergency
ADSC_CONFIRM = ["UM169an"] #confirm adsc armed
ADSC_DEVIATION = ["UM169f", "UM169t", "UM169v"] #route, level, speed
ADSC_SHUT_DOWN = ["UM169ao", "UM169at"]



class ReportsManager:
    def __init__(self, socket):
        self.socket = socket
        self.adsc_contracts = []
        self.position_reports = []
        self.index_reports = []
        self.monitoring_reports = []

    def add_position_report(self, report: PositionReport):
        self.position_reports.insert(0, report)
        self.socket.send("position_report", report)

