from datetime import datetime, timezone

class FlightStatus:
    def __init__(self):
        self.altitude = None
        self.position = {"lat": None, "lon": None}
        self.remaining_fuel = None
        self.temperature = None
        self.wind = None
        self.turbulence = None
        self.speed = None
        self.icing = None
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
