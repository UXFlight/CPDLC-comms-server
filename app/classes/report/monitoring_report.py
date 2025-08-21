from dataclasses import dataclass

@dataclass
class MonitoringReport:
    facility: str
    facility_designation: str
    facility_name: str
    vhf: str
    ref: str