from app.classes.report.position_report import PositionReport
from app.utils.time_utils import get_current_timestamp

def position_report_build(data, current_fix):
    routine = data["route"]
    position_report = PositionReport(
        positioncurrent=routine[current_fix]["fix"],
        timeatpositioncurrent_sec=routine[current_fix-1 if current_fix-1 >= 0 else 0]["elapsed_time_sec"],
        altitude_ft=routine[current_fix]["altitude_ft"],
        fixnext=routine[current_fix + 1]["fix"] if current_fix + 1 < len(routine) else None,
        timeatafixnext_sec=routine[current_fix + 1 if current_fix + 1 < len(routine) else len(routine)-1]["elapsed_time_sec"],
        fixnextplusone=routine[current_fix+2]["fix"] if current_fix + 2 < len(routine) else None,
        timeatedestination_sec=get_current_timestamp() + data["final_duration"],
        remainingfuel_kg=routine[current_fix]["fuel_kg"],
        temperature_c=routine[current_fix]["temperature"],
        winds={ "winddirection_deg": routine[current_fix]["wind"]["direction"], "speed_kmh": routine[current_fix]["wind"]["speed"] },
        turbulence=routine[current_fix]["turbulence"],
        icing=routine[current_fix]["icing"],
        speed_kmh=routine[current_fix]["speed_kmh"],
        speedground_kmh=routine[current_fix]["speed_kmh"] - routine[current_fix]["wind"]["speed"],
        #verticalchange=None,
        #trackangle_deg=routine[current_fix]["track_angle"],
        trueheading_deg=routine[current_fix]["heading_deg"],
        distance_km=routine[current_fix]["distance_km"]
        #supplementaryinformation=routine[current_fix]["supplementary_information"],
        #reportedwaypointposition=routine[current_fix]["reported_waypoint_position"],
        #reportedwaypointtime_sec=routine[current_fix]["reported_waypoint_time"],
        #reportedwaypointaltitude_ft=routine[current_fix]["reported_waypoint_altitude"],
    )
    return position_report.__dict__
