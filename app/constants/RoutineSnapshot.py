
from dataclasses import dataclass


@dataclass(frozen=True)
class RoutineSnapshot:
    current_fix: str
    acceleration: int
    tick_interval: float
    running: bool

