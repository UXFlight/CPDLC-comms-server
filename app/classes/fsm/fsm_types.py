# fsm_types.py
from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, List

from app.classes.log_entry.log_entry import LogEntry

Role = Literal["PILOT", "ATC"]

@dataclass
class Msg:
    log_entry: LogEntry
    role: Role         # "PILOT" ou "ATC"

@dataclass
class Transition:
    # Messages ATC envoyés automatiquement à l'entrée de l'état
    atc_opening: Optional[List[Msg]] = None

    # DM attendu (strict). "__ANY__" = on accepte tout (on regarde alors branches)
    expected: str  = "__ANY__"

    # Réponses ATC à renvoyer lorsque le DM attendu arrive
    atc_replies: Optional[List[Msg]] = field(default_factory=list)

    # S'il n'y a pas de branches, on passe ici après atc_replies
    next_state: Optional[str] = None

    # Branches : {pilot_ref -> state_id}
    branches: Optional[Dict[str, str]] = None

    # Délai d’inactivité (ms) avant un rappel (ex: STANDBY)
    timeout_ms: Optional[int] = 5000

# Un scénario = graphe
Scenario = Dict[str, Transition]
