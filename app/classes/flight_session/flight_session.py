from app.classes.atc.atc import Atc
from app.classes.flight_status.flight_status import FlightStatus
from app.classes.pilot.pilot import Pilot
from app.classes.routine.routine import Routine
from app.managers.logs_manager.logs_manager import LogsManager
from app.managers.reports_manager import ReportsManager


class FlightSession:
    def __init__(self, routine, pilot_id, atc_id, mongodb, socket):
        self.flight_id = routine["flight_id"]
        self.departure = routine["departure"]
        self.arrival = routine["arrival"]
        self.pilot = Pilot(pilot_id)
        self.atc = Atc(atc_id)
        self.status = FlightStatus(routine["route"], mongodb)
        self.reports = ReportsManager(socket, self.status, pilot_id)
        self.logs = LogsManager(mongodb, socket, self.reports)
        self.routine = Routine(routine, socket, self.status, pilot_id, self.logs, self.reports)
        self.route = routine["route"]
        self.current_data_authority = atc_id
        self.next_data_authority = None
        self.reports.set_snapshot_provider(self.routine.snapshot) 

    def to_dict(self):
        return {
            "flight_id": self.flight_id,
            "departure": self.departure,
            "arrival": self.arrival,
            "pilot": self.pilot.to_dict(),
            "status": self.status.to_dict(),
            "logs": self.logs.to_dict(),
            "route": self.route,
            "CDA": self.current_data_authority,
            "NDA": "ATC2",
        }
    
    def temp_route(self, waypoint):
        if not self.route:
            return []

        for i, point in enumerate(self.route):
            if point.get("fix") == waypoint:
                temp_route = self.route[i:] 
                return temp_route
        return []

    def get_route(self) :
        return [fix["fix"] for fix in self.routine.routine]

    def load_route(self, route):
        self.route = route
        return self.route

    def print_test(self):
        print(f"Flight ID: {self.flight_id}")
        print(f"Departure: {self.departure}")
        print(f"Arrival: {self.arrival}")
        print(f"Pilot ID: {self.pilot.id}")
        print(f"Status: {self.status.to_dict()}")
        print(f"Route: {self.route}")
        print(f"Current Data Authority: {self.current_data_authority}")
        print(f"Next Data Authority: {self.next_data_authority}")