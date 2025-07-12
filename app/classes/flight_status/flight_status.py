from datetime import datetime, timezone

from app.classes.log_entry.log_entry import LogEntry

class FlightStatus:
    def __init__(self, mongodb):
        self.mongodb = mongodb
        self.altitude = 35000
        self.position = {"lat": None, "lon": None}
        self.remaining_fuel = 7500
        self.temperature = -52
        self.wind = {"direction": 270, "speed": 85} 
        self.turbulence = "MODERATE"
        self.speed = 470  
        self.icing = "NONE"
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


            

