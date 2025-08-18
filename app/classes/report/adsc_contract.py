
from dataclasses import dataclass

@dataclass
class AdscData:
    type: str
    time: str
    value: str

class ADSCContract:
    def __init__(self, id: str, center: str, period: int, time_Next: int, trigger: str, is_active: bool = True):
        self.id = id
        self.center = center
        self.period = period
        self.time_Next = time_Next
        self.trigger = trigger
        self.is_active = is_active
        self.data = [AdscData]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "center": self.center,
            "period": int(self.period),        
            "time_Next": int(self.time_Next),   
            "trigger": self.trigger,         
            "is_Active": bool(self.is_active),
        }

    def add_data(self, type: str, time: str, value: float):
        self.data.append(AdscData(type=type, time=time, value=value))