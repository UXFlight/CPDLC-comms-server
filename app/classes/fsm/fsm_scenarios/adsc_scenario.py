from app.classes.fsm.fsm_types import Msg, Scenario, Transition
from app.database.mongo_db import MongoDb
from app.managers.logs_manager.logs_manager import LogsManager

mongodb = MongoDb()

SCENARIO_ADSC_EMERG: Scenario = {
    "atc_entry": Transition(
        atc_opening=[
            Msg(log_entry={"ref": "UM169ak", "text": "CONFIRM ADS-C EMERGENCY"}, role="ATC"),
        ],
        expected="__ANY__",                   # on attend une réponse du pilote
        branches={
            "DM67ab": "pilot_reset_ok",   
            "DM66": "due_to_perf",            # pilote: DUE TO ACFT PERF
            "DM65": "due_to_weather"          # pilote: DUE TO WEATHER
        },
    ),

    "pilot_entry": Transition(
        expected="DM67ab", # pilote: ADS‑C RESET
        atc_replies=[
            Msg(log_entry={"ref": "UM3", "text": "ROGER ADS-C RESET."}, role="ATC")
        ],
        next_state="end",
    ),

    "pilot_reset_ok": Transition(
        expected="DM67ab", 
        atc_replies=[
            Msg(log_entry={"ref": "UM3", "text": "ROGER ADS‑C RESET. EMERGENCY CANCELLED."}, role="ATC")
        ],
        branches={
            "DM0": "adsc_on_wilco",
            "DM66": "due_to_perf"
        },
    ),

    "adsc_on_wilco": Transition(
        expected="DM0",
        next_state="end",
    ),

    "due_to_perf": Transition(
        expected="DM66",
        atc_replies=[
            Msg(log_entry={"ref": "UM227", "text": "ACKNOWLEDGED DUE TO ACFT PERFORMANCE"}, role="ATC"),
            Msg(log_entry={"ref": "UM19", "text": "MAINTAIN PRESENT ALTITUDE"}, role="ATC"),
        ],
        next_state="adsc_on_wilco",
    ),
    "due_to_weather": Transition(
        expected="DM65",
        atc_replies=[
            Msg(log_entry={"ref": "UM227", "text": "ACKNOWLEDGED DUE TO WEATHER"}, role="ATC"),
        ],
        next_state="adsc_on_wilco",
    ),

    "end": Transition(
        expected="__ANY__",
        atc_replies=[],
        next_state=None,
    ),
}
