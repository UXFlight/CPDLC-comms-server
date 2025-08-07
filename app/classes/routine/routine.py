import asyncio
from app.classes.flight_status.flight_status import FlightStatus
from enum import Enum

class Speed(Enum):
    SLOW = 50
    MEDIUM = 100
    FAST = 150
    EXTREME = 300

class Routine:
    def __init__(self, routine, socket, flight_status: FlightStatus, room, logs):
        self.routine = routine["route"]
        self.flight_status = flight_status
        self.socket = socket
        self.room = room
        self.logs = logs
        self.acceleration = 100
        self.tick_interval = 1
        self.elapsed_simulated = 0
        self.current_fix = 0
        self.distance_in_segment = 0 
        self.running = False
        self.stepping = False
        self._stop_signal = False

        distances = [fix["distance_km"] for fix in self.routine]
        self.socket.send("routine_load", {
            "total_distance": self.routine[-1]["total_distance"],
            "distances": distances
        }, room=self.room)

    def simulation_speed(self, speed: Speed):
        self.acceleration = speed.value

    async def simulate_flight_progress(self):
        self.running = True
        self._stop_signal = False

        while self.current_fix < len(self.routine)-1: # self.elapsed_simulated < self.routine[-1]["elapsed_time_sec"]:
            if self._stop_signal:
                print("Simulation paused.")
                break

            await asyncio.sleep(self.tick_interval)

            self.elapsed_simulated += self.tick_interval * self.acceleration
            distance_increment = self.calculate_distance()
            self.distance_in_segment += distance_increment

            current_fix_obj = self.routine[self.current_fix]
            fix_distance = current_fix_obj["distance_km"]

            if self.distance_in_segment >= fix_distance:
                if self.current_fix < len(self.routine) - 1:
                    self.current_fix += 1
                    self.update_flight_status()
                else:
                    self.update_flight_status(end=True)
                    self.socket.send("plane_arrival", self.flight_status.to_dict(), room=self.room)
                    break
                self.distance_in_segment = 0
                self.socket.send("waypoint_change", {
                    "flight": self.flight_status.to_dict(),
                    "currentFixIndex": self.current_fix,
                }, room=self.room)
            else:
                self.flight_status.update({
                    "distance": round(self.routine[self.current_fix]["total_distance"] - fix_distance + self.distance_in_segment, 2),
                    "fix_distance": int(self.distance_in_segment),
                    "elapsed_time_sec": int(self.elapsed_simulated),
                })
                self.socket.send("plane_partial_progress", self.flight_status.to_dict(), room=self.room)

    def calculate_distance(self):
        current_speed = self.routine[self.current_fix]["speed_kmh"]
        return current_speed * self.acceleration / 3600  # km/h → km/sec * seconds

    def update_flight_status(self, end=False):
        if not end: 
            fix = self.routine[self.current_fix]
        else:
            fix = self.routine[-1]
        self.flight_status.update({
            "altitude": fix.get("altitude_ft", 0),
            "distance": fix.get("total_distance", 0),
            "fix_distance": 0,
            "elapsed_time_sec": int(self.elapsed_simulated),
            "remaining_fuel": fix.get("fuel_kg", 0),
            "temperature": fix.get("temperature", 0),
            "wind": fix.get("wind", {"direction": 0, "speed_kmh": 0}),
            "turbulence": fix.get("turbulence", "NONE"),
            "speed": fix.get("speed_kmh", 0),
            "icing": fix.get("icing", "NONE"),
        })

    @staticmethod
    def run_async_in_thread(coroutine):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coroutine)

        #threading.Thread(target=runner).start()

    def update_routine(self, new_routine):
        self.running = False 
        arrival_fix = self.routine[-1]
        new_routine_fixes = {fix["fix"] for fix in new_routine}
        self.routine = list(filter(lambda fix: fix["fix"] in new_routine_fixes, self.routine))
        self.routine.append(arrival_fix)
        self.normalize_routine()

        self.elapsed_simulated = 0
        self.current_fix = 0
        self.distance_in_segment = 0
        self.running = True

        distances = [fix["distance_km"] for fix in self.routine]
        self.socket.send("routine_load", {
            "total_distance": self.routine[-1]["total_distance"],
            "distances": distances
        }, room=self.room)
        print(f"Routine updated: {self.routine}")
        print(f"distances time reset to {distances} km")

        Routine.run_async_in_thread(self.simulate_flight_progress())


        # new_routine_fixes = {fix["fix"] for fix in new_routine}
        # self.routine = list(filter(lambda fix: fix["fix"] in new_routine_fixes, self.routine))
        # self.elapsed_simulated = 0
        # self.current_fix = 0
        # self.distance_in_segment = 0
        
        # distances = [fix["distance_km"] for fix in self.routine]
        # self.socket.send("routine_load", {
        #     "total_distance": self.routine[-1]["total_distance"],
        #     "distances": distances
        # }, room=self.room)
        # self.simulate_flight_progress()
    
    # def available_messages(self):
    #     return self.routine[self.current_fix].get("atc_messages", None)
    
    # def check_priority_message(self):
    #     if self.available_messages:
    #         self.available_messages enumerate
            

    # def simulate_um_message(self):
    #     if not self.available_messages():
    #         return None
    #     else:
            
    # ACTIONS
    def pause(self):
        self._stop_signal = True
        self.running = False

    def play(self):
        if not self.running:
            self.socket.start_background_task(asyncio.run, self.simulate_flight_progress())
            
    def step_forward(self):
        if self.current_fix < len(self.routine) - 1:
            self.current_fix += 1
            self.update_flight_status()
            self.socket.send("waypoint_change", {
                "flight": self.flight_status.to_dict(),
                "currentFixIndex": self.current_fix
            }, room=self.room)

    def step_back(self):
        if self.current_fix > 0:
            self.current_fix -= 1
            self.update_flight_status()
            self.socket.send("waypoint_change", {
                "flight": self.flight_status.to_dict(),
                "currentFixIndex": self.current_fix
        }, room=self.room)
