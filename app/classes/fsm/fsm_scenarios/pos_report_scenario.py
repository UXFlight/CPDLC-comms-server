from app.classes.fsm.fsm_types import Msg, Scenario, Transition

SCENARIO_REQ_POSITION_REPORT: Scenario = {
    "atc_entry": Transition(
        atc_opening=[
            Msg(log_entry={"ref": "UM147", "text": "REQUEST POSITION REPORT"}, role="ATC"),
        ],
        branches={
            "DM48": "pilot_position_report",  # POSITION REPORT
            "DM1":  "pilot_unable",           # UNABLE
        },
    ),

    "pilot_position_report": Transition(
        expected="DM48",
        atc_replies=[Msg(log_entry={"ref": "UM3", "text": "ROGER POSITION REPORT"}, role="ATC")],
        next_state="end",
    ),

    # "pilot_standby": Transition(
    #     expected="DM2",
    #     atc_replies=[Msg(log_entry={"ref": "UM3", "text": "ROGER STANDBY"}, role="ATC")],
    #     # On attend le DM48 ensuite
    #     branches={
    #         "DM48": "pilot_position_report",
    #         "DM1":  "pilot_unable",
    #     },
    #     # timeout_ms=45000,  # si tu veux relancer UM147 via ton handler de timeout
    # ),

    "pilot_unable": Transition(
        expected="DM1",
        atc_replies=[Msg(log_entry={"ref": "UM3", "text": "ROGER UNABLE"}, role="ATC")],
        next_state="end",
    ),

    "end": Transition(expected="__ANY__", atc_replies=[], next_state=None),
}