from app.classes.fsm.fsm_types import Msg, Scenario, Transition

SCENARIO_ADSC_CONFIRM_ARMED: Scenario = {
    "atc_entry": Transition(
        atc_opening=[
            Msg(log_entry={"ref": "UM169an", "text": "CONFIRM ADS-C ARMED"}, role="ATC"),
        ],
        expected="__ANY__",
        branches={
            "DM0": "pilot_wilco",
        },
    ),

    "pilot_wilco": Transition(
        expected="DM0",
        atc_replies=[Msg(
                log_entry={
                    "ref": "UM169aw",
                    "text": "RESUME NORMAL ADS-C OPERATIONS. CPDLC AND VOICE POSITION REPORTS NOT REQUIRED"
                },
                role="ATC"
            ),],
        next_state="pilot_wilco2",
    ),

  
    "pilot_wilco2": Transition(
        expected="DM0",
        next_state="end",
    ),

    "end": Transition(expected="__ANY__", atc_replies=[], next_state=None),
}

