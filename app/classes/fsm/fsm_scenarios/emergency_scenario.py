from app.classes.fsm.fsm_types import Msg, Scenario, Transition

SCENARIO_EMERGENCY: Scenario = {
    # Le pilote initie l'urgence (PAN ou MAYDAY).
    # On route selon le DM reçu.
    "pilot_entry": Transition(
        expected="__ANY__",
        branches={
            "DM55": "pan_received",     # PAN PAN PAN
            "DM56": "mayday_received",  # MAYDAY MAYDAY MAYDAY
        },
    ),

    # Réception PAN → ATC accuse réception via CPDLC
    "pan_received": Transition(
        expected="DM55",
        atc_replies=[
            # 4.8.2.3(a) : UM169r ROGER PAN
            Msg(log_entry={"ref": "UM169r", "text": "ROGER PAN"}, role="ATC"),
        ],
        next_state="end",
    ),

    # Réception MAYDAY → ATC accuse réception via CPDLC
    "mayday_received": Transition(
        expected="DM56",
        atc_replies=[
            # 4.8.2.3(b) : UM169q ROGER MAYDAY
            Msg(log_entry={"ref": "UM169q", "text": "ROGER MAYDAY"}, role="ATC"),
        ],
        next_state="end",
    ),

    # Fin
    "end": Transition(
        expected="__ANY__",
        atc_replies=[],
        next_state=None,
    ),
}
