from datetime import datetime, timezone

from app.classes.log_entry.log_entry import LogEntry
from app.database.flight_plan.routine import routine

class FlightStatus:
    def __init__(self, mongodb):
        self._mongodb = mongodb
        self.altitude = routine[0].get("altitude_ft", 0)
        self.position = {"lat": None, "lon": None}
        self.current_distance = 0
        self.fix_distance = 0
        self.total_time_sec = 0
        self.remaining_fuel = routine[0].get("fuel_kg", 000)
        self.temperature = routine[0].get("temperature", 00)
        self.wind = routine[0].get("wind", {"direction": 0, "speed_kmh": 0})
        self.turbulence = routine[0].get("turbulence", "NONE")
        self.speed = routine[0].get("speed_kmh", 470)
        self.icing = routine[0].get("icing", "NONE")
        self.connections = {
            "CPDLC": "CONNECTED",
            "COMMUNICATION": "CONNECTED",
            "AFN_CONNECTING": "AVAILABLE",
            "ATN_AVAILABILITY": "AVAILABLE"
        }
        self.updated_at = datetime.now(timezone.utc)

    def update(self, data):
        self.altitude = data.get("altitude", self.altitude)
        self.position = data.get("position", self.position)
        self.current_distance = data.get("distance", self.current_distance)
        self.fix_distance = data.get("fix_distance", self.fix_distance)
        self.total_time_sec = data.get("elapsed_time_sec", self.total_time_sec)
        self.remaining_fuel = data.get("remaining_fuel", self.remaining_fuel)
        self.temperature = data.get("temperature", self.temperature)
        self.wind = data.get("wind", self.wind)
        self.turbulence = data.get("turbulence", self.turbulence)
        self.speed = data.get("speed", self.speed)
        self.icing = data.get("icing", self.icing)
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "altitude": self.altitude,
            "position": self.position,
            "current_distance": self.current_distance,
            "fix_distance": self.fix_distance,
            "total_time_sec": self.total_time_sec,
            "remaining_fuel": self.remaining_fuel,
            "temperature": self.temperature,
            "wind": self.wind,
            "turbulence": self.turbulence,
            "speed": self.speed,
            "icing": self.icing,
            "connections" : self.connections,
            "updated_at": self.updated_at.isoformat()
        }

    # def update_parameter(self, log: LogEntry):
    #     datalink = self.mongodb.find_datalink_by_ref(log.ref)
    #     categoty = datalink.get("Category", "")
    #     if "Vertical" in categoty:
    #         self.update_altitude()


    # def update_altitude(self, altitude):
    #     if altitude != self.altitude:
    #         self.previous_altitude = self.altitude
    #         self.altitude = altitude
    #         self.updated_at = datetime.now(timezone.utc)

######################################### ROUTINE ##########################################################
    

