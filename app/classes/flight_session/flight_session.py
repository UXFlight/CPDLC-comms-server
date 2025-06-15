from app.classes.atc.atc import Atc
from app.classes.flight_status.flight_status import FlightStatus
from app.classes.pilot.pilot import Pilot
from app.managers.logs_manager.logs_manager import LogsManager


class FlightSession:
    def __init__(self, flight_id, departure, arrival, pilot_id, atc_id):
        self.flight_id = flight_id
        self.departure = departure
        self.arrival = arrival
        self.pilot = Pilot(pilot_id)
        self.atc = Atc(atc_id)
        self.status = FlightStatus()
        self.logs = LogsManager()
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
            "CDA": self.current_data_authority,
            "NDA": self.next_data_authority,
        }
