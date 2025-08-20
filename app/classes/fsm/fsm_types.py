# fsm_types.py
from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, List

from app.classes.log_entry.log_entry import LogEntry

Role = Literal["PILOT", "ATC"]

@dataclass
class Msg:
    log_entry: {"ref": str, "text": str} # type: ignore
    role: Role         # "PILOT" ou "ATC"

@dataclass
class Transition:
    atc_opening: Optional[List[Msg]] = None
    expected: str  = "__ANY__"
    atc_replies: Optional[List[Msg]] = field(default_factory=list)
    next_state: Optional[str] = None
    branches: Optional[Dict[str, str]] = None
    timeout_ms: Optional[int] = 90000

# scenario = graphe
Scenario = Dict[str, Transition]
