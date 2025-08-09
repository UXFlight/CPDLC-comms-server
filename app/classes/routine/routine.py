import asyncio
from app.classes.flight_status.flight_status import FlightStatus
from enum import Enum

from app.managers.logs_manager.logs_manager import LogsManager

class Speed(Enum):
    SLOW = 10
    MEDIUM = 30
    FAST = 60
    EXTREME = 100

class Routine:
    def __init__(self, routine, socket, flight_status: FlightStatus, room, logs: LogsManager):
        self.routine = routine["route"]
        self.flight_status = flight_status
        self.socket = socket
        self.room = room
        self.logs = logs
        self.acceleration = Speed.MEDIUM.value
        self.tick_interval = 1
        self.elapsed_simulated = 0
        self.current_fix = 0
        self.distance_in_segment = 0 
        self.running = False
        self.stepping = False
        self._stop_signal = False
        self.visited_messages = []

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
            await self.simulate_um_message()

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
    
    def available_messages(self):
        msgs = self.routine[self.current_fix].get("atc_messages") or []
        return len(msgs) > 0

    async def simulate_um_message(self):
        if not self.available_messages():
            return
        else:
            for message in self.routine[self.current_fix]["atc_messages"]:
                if message['message']['id'] in self.visited_messages:
                    #event only for debugging
                    self.socket.send("message_visited", message["message"], room=self.room)
                    continue
                if (message["at_position"] <= self.distance_in_segment):
                    new_log = self.logs.add_log(message["message"])
                    print(f"Message {self.logs.get_logs()} added to logs.")
                    self.visited_messages.append(f"{new_log.id}")
                    self.socket.send("log_added", new_log.to_dict(), room=self.room)

    def remove_um_message(self, fix):
        print(f"Removing messages for fix: {fix}")
        messages_to_be_removed = [msg for msg in self.visited_messages if msg.startswith(f"{fix}")]
        print(f"Messages to be removed: {messages_to_be_removed}")
        for log in self.logs.logs:
            if log.id in messages_to_be_removed:
                self.visited_messages.remove(f"{log.id}")
                self.logs.remove_log_by_id(log.id)

        self.socket.send("removed_logs", self.logs.get_logs(), room=self.room)

    # ACTIONS
    def pause(self):
        self._stop_signal = True
        self.running = False

    def play(self):
        if not self.running:
            self.socket.start_background_task(asyncio.run, self.simulate_flight_progress())

    def step_forward(self):
        self.pause()
        if self.current_fix < len(self.routine) - 1:
            self.current_fix += 1
            self.distance_in_segment = 0
            self.update_flight_status()
            self.socket.send("waypoint_change", {
                "flight": self.flight_status.to_dict(),
                "currentFixIndex": self.current_fix
            }, room=self.room)
        self.play()

    def step_back(self):
        self.pause()
        if self.current_fix > 0:
            self.current_fix -= 1

        self.remove_um_message(self.routine[self.current_fix]["fix"])
        self.distance_in_segment = 0
        self.update_flight_status()
        self.socket.send("waypoint_change", {
            "flight": self.flight_status.to_dict(),
            "currentFixIndex": self.current_fix
        }, room=self.room)
        self.play()
