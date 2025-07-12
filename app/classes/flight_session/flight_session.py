from app.classes.atc.atc import Atc
from app.classes.flight_status.flight_status import FlightStatus
from app.classes.pilot.pilot import Pilot
from app.database.flight_plan import flight_plan
from app.database.mongo_db import MongoDb
from app.managers.logs_manager.logs_manager import LogsManager


class FlightSession:
    def __init__(self, flight_id, departure, arrival, pilot_id, route, atc_id, mongodb):
        self.flight_id = flight_id
        self.departure = departure
        self.arrival = arrival
        self.pilot = Pilot(pilot_id)
        self.atc = Atc(atc_id)
        self.status = FlightStatus(mongodb)
        self.mongodb = mongodb
        self.logs = LogsManager(mongodb)
        self.route = route
        self.current_data_authority = atc_id
        self.next_data_authority = None

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
    
    def load_route(self, waypoint):
        if not self.route:
            return []

        for i, point in enumerate(self.route):
            if point.get("fix") == waypoint:
                self.route = self.route[i:]  # garde du point trouvé jusqu'à la fin
                return self.route

        # Si aucun point ne correspond
        print(f"Waypoint '{waypoint}' non trouvé dans la route.")
        return []

    def print_test(self):
        print(f"Flight ID: {self.flight_id}")
        print(f"Departure: {self.departure}")
        print(f"Arrival: {self.arrival}")
        print(f"Pilot ID: {self.pilot.id}")
        print(f"Status: {self.status.to_dict()}")
        print(f"Route: {self.route}")
        print(f"Current Data Authority: {self.current_data_authority}")
        print(f"Next Data Authority: {self.next_data_authority}")