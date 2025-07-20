import asyncio
from app.database.flight_plan.routine import routine

class Routine:
    def __init__(self, socket, flight_status, room):
        self.routine = routine
        self.flight_status = flight_status
        self.socket = socket
        self.room = room
        self.acceleration = 60  # 1s = 60s simulées
        self.tick_interval = 1  # 1s réelle
        self.elapsed_simulated = 0
        self.total_distance = 0
        self.current_fix = 0

    async def simulate_flight_progress(self):
        while self.elapsed_simulated < self.routine[-1]["elapsed_time_sec"]:
            await asyncio.sleep(self.tick_interval)

            # Simule le temps (accéléré)
            self.elapsed_simulated += self.tick_interval * self.acceleration

            # Si on change de waypoint
            if self.current_fix < len(self.routine) - 1 and self.elapsed_simulated >= self.routine[self.current_fix + 1]["elapsed_time_sec"]:
                self.current_fix += 1
                self.update_flight_status()
                await self.socket.send("plane_partial_progress", self.flight_status.to_dict(), room=self.room)
            else:
                # Distance intermédiaire dans le segment actuel
                distance = self.calculate_distance()
                self.total_distance = distance  # total distance = segment cumulative
                self.flight_status.update({
                    "distance": round(self.total_distance, 2),
                    "elapsed_time_sec": int(self.elapsed_simulated),
                })
                await self.socket.send("plane_waypoint_progress", self.flight_status.to_dict(), room=self.room)

        # Fin de vol
        self.update_flight_status(end=True)
        await self.socket.send("plane_arrival", self.flight_status.to_dict(), room=self.room)

    def calculate_distance(self):
        current_speed = self.routine[self.current_fix]["speed_kmh"]
        distance = current_speed * self.acceleration / 3600
        return distance

    def update_flight_status(self, end=False):
        if end:
            # Dernier état (avion au sol)
            self.flight_status.update({
                "altitude": 0,
                "distance": self.routine[-1].get("total_distance", self.total_distance),
                "elapsed_time_sec": self.elapsed_simulated,
                "remaining_fuel": self.routine[-1].get("fuel_kg", 0),
                "temperature": 15,
                "wind": {"direction": 0, "speed_kmh": 0},
                "turbulence": "NONE",
                "speed": 0,
                "icing": "NONE"
            })
        else:
            fix = self.routine[self.current_fix]
            self.flight_status.update({
                "altitude": fix.get("altitude_ft", 0),
                "distance": fix.get("total_distance", self.total_distance),
                "elapsed_time_sec": self.elapsed_simulated,
                "remaining_fuel": fix.get("fuel_kg", 0),
                "temperature": fix.get("temperature", 0),
                "wind": fix.get("wind", {"direction": 0, "speed_kmh": 0}),
                "turbulence": fix.get("turbulence", "NONE"),
                "speed": fix.get("speed_kmh", 0),
                "icing": fix.get("icing", "NONE"),
            })
