import asyncio
from dataclasses import dataclass
from app.classes.flight_status.flight_status import FlightStatus
from enum import Enum

from app.classes.fsm.fsm_scenarios.climb_and_report_scenario import SCENARIO_CLIMB_AND_REPORT_MAINTAINING
from app.classes.fsm.fsm_scenarios.fsm_scenario_manager import FsmScenarioManager
from app.classes.fsm.fsm_scenarios.pos_report_scenario import SCENARIO_REQ_POSITION_REPORT
from app.classes.fsm.fsm_types import Scenario
from app.constants.RoutineSnapshot import RoutineSnapshot
from app.managers.logs_manager.logs_manager import LogsManager
from app.managers.reports_manager import ReportsManager
from app.utils.position_report_build import position_report_build

class Speed(Enum):
    SLOW = 30
    MEDIUM = 60
    FAST = 100
    EXTREME = 200

SCENARIO_REGISTRY: dict[str, Scenario] = {
    "SCENARIO_REQ_POSITION_REPORT": SCENARIO_REQ_POSITION_REPORT,
    "SCENARIO_CLIMB_AND_REPORT_MAINTAINING": SCENARIO_CLIMB_AND_REPORT_MAINTAINING
}


class Routine:
    def __init__(self, routine, socket, flight_status: FlightStatus, room, logs: LogsManager, reports: ReportsManager, scenarios: FsmScenarioManager):
        self.routine = routine
        self.route = routine["route"]
        self.flight_status = flight_status
        self.socket = socket
        self.room = room
        self.logs = logs
        self.reports = reports
        self.scenarios = scenarios
        self.acceleration = Speed.MEDIUM.value
        self.tick_interval = 1
        self.elapsed_simulated = 0
        self.current_fix = 0
        self.distance_in_segment = 0 
        self.running = False
        self.stepping = False
        self._stop_signal = False
        self.visited_messages = []
        self._stop_event = None

        distances = [fix["distance_km"] for fix in self.route]
        self.socket.send("routine_load", {
            "total_distance": self.route[-1]["total_distance"],
            "distances": distances
        }, room=self.room)

    def set_new_route(self, new_route):
        self.route = new_route
        distances = [fix["distance_km"] for fix in new_route]

        self.socket.send("routine_load", {
            "total_distance": self.route[-1]["total_distance"],
            "distances": distances,
            "current_fix": self.current_fix
        }, room=self.room)

    def simulation_speed(self, speed: Speed):
        self.acceleration = speed.value

    async def simulate_flight_progress(self):
        self._stop_event = asyncio.Event()
        self.running = True
        self._stop_signal = False

        while self.current_fix < len(self.route)-1: # self.elapsed_simulated < self.route[-1]["elapsed_time_sec"]:
            try:
                # attend tick_interval OU un stop (ce qui arrive en premier)
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.tick_interval)
                # si on arrive ici sans TimeoutError, c'est que stop() a été appelé
                break
            except asyncio.TimeoutError:
                pass  # pas de stop, on exécute le "tick" normal

            #await asyncio.sleep(self.tick_interval)

            self.elapsed_simulated += self.tick_interval * self.acceleration
            distance_increment = self.calculate_distance()
            self.distance_in_segment += distance_increment

            current_fix_obj = self.route[self.current_fix]
            fix_distance = current_fix_obj["distance_km"]
            await self.simulate_um_message()

            if self.distance_in_segment >= fix_distance:
                if self.current_fix < len(self.route) - 1:
                    self.current_fix += 1
                    self.update_flight_status()
                else:
                    self.update_flight_status(end=True)
                    self.socket.send("plane_arrival", self.flight_status.to_dict(), room=self.room)
                    break
                self.socket.send("waypoint_change", {
                    "flight": self.flight_status.to_dict(),
                    "currentFixIndex": self.current_fix,
                }, room=self.room)
                self.distance_in_segment = 0

                position_report = position_report_build(self.routine, self.current_fix)
                self.reports.add_position_report(position_report)
            else:
                self.flight_status.update({
                    "distance": round(self.route[self.current_fix]["total_distance"] - fix_distance + self.distance_in_segment, 2),
                    "fix_distance": int(self.distance_in_segment),
                    "elapsed_time_sec": int(self.elapsed_simulated),
                })
                self.socket.send("plane_partial_progress", self.flight_status.to_dict(), room=self.room)

    def calculate_distance(self):
        current_speed = self.route[self.current_fix]["speed_kmh"]
        return current_speed * self.acceleration / 3600  # km/h → km/sec * seconds

    def update_flight_status(self, end=False):
        if not end: 
            fix = self.route[self.current_fix]
        else:
            fix = self.route[-1]
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
    
    def concerned_messages(self, fix=None):
        all_msgs = []
        if not fix:  # pour ajouter les logs suite a un step + 1
            curr_fix = self.current_fix if self.current_fix == 0 else self.current_fix-1
            for i in range(curr_fix, -1, -1):
                fix_msgs = self.route[i].get("atc_messages") or []
                all_msgs[:0] = fix_msgs 
        else:  # pour retirer les logs suite a un backup
            for i in range(len(self.route) - 1, self.current_fix - 1, -1):
                fix_msgs = self.route[i].get("atc_messages") or []
                all_msgs.extend(fix_msgs)
        return all_msgs if all_msgs else None

    def available_messages(self):
        msgs = self.route[self.current_fix].get("atc_messages") or []
        return len(msgs) > 0

    async def simulate_um_message(self):
        if not self.available_messages():
            return
        else:
            for message in self.route[self.current_fix]["atc_messages"]:
                if message['message']['id'] in self.visited_messages:
                    continue
                if (message["at_position"] <= self.distance_in_segment):
                    if "scenario" in message:
                        self.visited_messages.append(message['message']['id'])
                        self.handle_scenario(message)
                    else:
                        new_log = self.logs.create_add_log(message["message"])
                        self.visited_messages.append(f"{new_log.id}")
                        self.socket.send("log_added", new_log.to_dict(), room=self.room)

    def handle_scenario(self, message: dict):
        scenario_key = message.get("scenario")
        if not scenario_key:
            return

        scenario_obj = SCENARIO_REGISTRY.get(scenario_key)
        if scenario_obj:
            self.scenarios.start_scenario(
                scenario=scenario_obj,
                room=self.room,
                initiator="ATC",
            )

    def remove_um_message(self, fix):
        msgs = self.concerned_messages(fix)
        if not msgs:
            return
        msg_ids_to_remove = {msg["message"]["id"] for msg in msgs}
        for log_id in self.visited_messages[:]:
            if log_id in msg_ids_to_remove:
                self.visited_messages.remove(log_id)
                self.logs.remove_log_by_id(log_id)
                
        ids = [log.id for log in self.logs.logs]
        self.socket.send("removed_logs", self.logs.get_logs(), room=self.room)

    def add_um_message(self):
        msgs = self.concerned_messages()
        if not msgs:
            return
        for message in msgs:
            msg_id = message["message"]["id"]
            if msg_id not in self.visited_messages:
                new_log = self.logs.create_add_log(message["message"])
                self.visited_messages.append(f"{new_log.id}")
                self.socket.send("log_added", new_log.to_dict(), room=self.room)

    def pause(self):
        self._stop_signal = True
        self.reports.adsc_manager.stop_adsc_timer()
        self.running = False
        if self._stop_event:
            self._stop_event.set()

    def play(self):
        if not self.running:
            self._stop_signal = False
            self.reports.adsc_manager.start_adsc_timer()
            self._stop_event.clear()
            
            def _run_simulation():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.simulate_flight_progress())
                finally:
                    loop.close()
            
            self.socket.start_background_task(_run_simulation)

    def stop(self):
        self.running = False
        if self._stop_event:
            self._stop_event.set() 

    async def stop_and_wait(self, timeout: float = 2.0):
        self.stop()
        deadline = asyncio.get_running_loop().time() + timeout
        while self.running and asyncio.get_running_loop().time() < deadline:
            await asyncio.sleep(0)

    def step_forward(self):
        is_running_before_step = self.running
        if is_running_before_step:
            self.pause()
        if self.current_fix < len(self.route) - 1:
            self.current_fix += 1
            self.distance_in_segment = 0
            self.add_um_message()
            self.update_flight_status()
            position_report = position_report_build(self.routine, self.current_fix)
            self.reports.add_position_report(position_report)
            self.socket.send("waypoint_change", {
                "flight": self.flight_status.to_dict(),
                "currentFixIndex": self.current_fix
            }, room=self.room)
        if is_running_before_step:
            self.play()

    def step_back(self):
        is_running_before_step = self.running
        if is_running_before_step:
            self.pause()
        if self.current_fix > 0:
            self.current_fix -= 1

        self.remove_um_message(self.route[self.current_fix]["fix"])
        self.distance_in_segment = 0
        self.update_flight_status()
        position_report = position_report_build(self.routine, self.current_fix)
        self.reports.add_position_report(position_report)
        self.socket.send("waypoint_change", {
            "flight": self.flight_status.to_dict(),
            "currentFixIndex": self.current_fix
        }, room=self.room)
        if is_running_before_step:
            self.play()

    def snapshot(self) -> RoutineSnapshot:
        return RoutineSnapshot(
            current_fix=self.route[self.current_fix]["fix"],
            acceleration=self.acceleration,
            tick_interval=self.tick_interval,
            running=self.running
        )