from dataclasses import dataclass

@dataclass
class EmergencyReport:
    type: str
    reason: str
    divertTo: str
    descendAlt: str
    offsetTo: str
    soulsOnBoard: str
    fuel: str
    remarks: str
