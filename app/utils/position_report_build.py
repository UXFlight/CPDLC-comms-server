from app.classes.report.position_report import PositionReport
from app.utils.time_utils import format_timestamp_utc, get_current_timestamp_pos_report, parse_duration_to_seconds

def position_report_build(data, current_fix):
    routine = data["route"]
    final_duration_sec = parse_duration_to_seconds(data["final_duration"])

    position_report = PositionReport(
        positioncurrent=routine[current_fix]["fix"],
        timeatpositioncurrent_sec = format_timestamp_utc(get_current_timestamp_pos_report() + routine[current_fix]["elapsed_time_sec"]),
        altitude_ft=routine[current_fix]["altitude_ft"],
        fixnext=routine[current_fix + 1]["fix"] if current_fix + 1 < len(routine) else None,
        timeatafixnext_sec = (
            format_timestamp_utc(get_current_timestamp_pos_report() + routine[current_fix + 1]["elapsed_time_sec"])
            if current_fix + 1 < len(routine)
            else None
        ),
        fixnextplusone=routine[current_fix + 2]["fix"] if current_fix + 2 < len(routine) else None,
        timeatedestination_sec=format_timestamp_utc(get_current_timestamp_pos_report() + final_duration_sec),
        remainingfuel_kg=routine[current_fix]["fuel_kg"],
        temperature_c=routine[current_fix]["temperature"],
        winds={
            "winddirection_deg": routine[current_fix]["wind"]["direction"],
            "speed_kmh": routine[current_fix]["wind"]["speed"]
        },
        turbulence=routine[current_fix]["turbulence"],
        icing=routine[current_fix]["icing"],
        speed_kmh=routine[current_fix]["speed_kmh"],
        speedground_kmh=routine[current_fix]["speed_kmh"] - routine[current_fix]["wind"]["speed"],
        trueheading_deg=routine[current_fix]["heading_deg"],
        distance_km=routine[current_fix]["distance_km"]
    )

    # Optionnel : filtrer les champs None
    return {k: v for k, v in position_report.__dict__.items() if v is not None}