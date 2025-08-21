from app.classes.fsm.fsm_types import Msg, Scenario, Transition

SCENARIO_CLIMB_AND_REPORT_MAINTAINING: Scenario = {
    # 1) ATC délivre la clairance de montée
    "atc_entry": Transition(
        atc_opening=[
            Msg(
                log_entry={
                    "ref": "UM20",
                    "text": "CLIMB TO AND MAINTAIN FL370"
                },
                role="ATC",
            ),
        ],
        expected="__ANY__",
        branches={
            "DM0": "ack_climb_wilco",   # WILCO
            "DM3": "ack_climb_roger",   # ROGER
            "DM2": "ack_climb_standby", # STANDBY
            "DM1": "ack_climb_unable",  # UNABLE
        },
    ),

    "ack_climb_wilco": Transition(
        expected="DM0",
        atc_replies=[
            Msg(
                log_entry={
                    "ref": "UM129",
                    "text": "REPORT MAINTAINING FL370"
                },
                role="ATC",
            ),
        ],
        branches={
            "DM37": "resp_pil_maintaining"
        },
    ),
    "ack_climb_standby": Transition(
        expected="DM2",
        atc_replies=[
            Msg(log_entry={"ref": "UM3", "text": "ROGER STANDBY"}, role="ATC"),
        ],
        next_state="arm_report_level",  # on arme quand même la demande de report
    ),
    "ack_climb_unable": Transition(
        expected="DM1",
        atc_replies=[
            Msg(log_entry={"ref": "UM3", "text": "ROGER UNABLE"}, role="ATC"),
        ],
        next_state="end",
    ),

    "resp_pil_maintaining": Transition(
        expected="DM37",
        atc_replies=[
            Msg(log_entry={"ref": "UM3", "text": "ROGER MAINTAINING FL370"}, role="ATC"),
        ],
        next_state="end",
    ),

    "end": Transition(expected="__ANY__", atc_replies=[], next_state=None),
}
