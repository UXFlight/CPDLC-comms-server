import asyncio
from copy import deepcopy
from enum import Enum
from flask import request  # type: ignore
from app.classes import Socket  # type: ignore
from app.classes.report.position_report import PositionReport
from app.database.mongo_db import MongoDb
from app.managers.flight_manager.flight_manager import FlightManager
from app.database.flight_plan.flight_plan import flight_plan
from app.database.flight_plan.routine import routine
from app.utils.error_handler import handle_errors

class Speed(Enum):
    SLOW = 3
    MEDIUM = 6
    FAST = 10
    EXTREME = 20

class SocketGateway:
    def __init__(self, socket_service: Socket, flight_manager: FlightManager, mongodb: MongoDb):
        self.socket_service = socket_service
        self.flight_manager = flight_manager
        self.mongodb = mongodb

    def init_events(self):
        self.socket_service.listen('connect', self.on_connect)
        self.socket_service.listen('logon', self.on_logon)
        self.socket_service.listen('add_log', self.on_add_log)
        self.socket_service.listen('change_status', self.on_change_status)
        self.socket_service.listen('is_loadable', self.on_is_loadable)
        self.socket_service.listen('load_fms', self.on_load_fms)
        self.socket_service.listen('execute_route', self.on_execute_route)
        self.socket_service.listen('routine_play', self.on_routine_play)
        self.socket_service.listen('routine_pause', self.on_routine_pause)
        self.socket_service.listen('routine_step_back', self.on_routine_step_back)
        self.socket_service.listen('routine_step_forward', self.on_routine_step_forward)
        self.socket_service.listen('routine_set_speed', self.on_routine_set_speed)
        self.socket_service.listen('disconnect', self.on_disconnect)

    def on_connect(self, auth=None):
        print(f"Client connected with auth: {auth}")
        sid = request.sid
        flight = self.flight_manager.create_session(routine, sid, self.mongodb, self.socket_service)
        self.socket_service.send("connected", flight.to_dict(), room=sid)

    def on_logon(self, data: dict):
        sid = request.sid
        atc_available = self.mongodb.find_available_atc(data.get("username"))
        print(f"ATC available: {atc_available}")
        if atc_available:
            flight = self.flight_manager.get_session(sid)
            flight.atc_id = data.get("username")
            self.socket_service.send("logon_success", data={}, room=sid)
            self.socket_service.send("load_logs", flight.logs.get_logs(), room=sid)
            self.socket_service.send("load_adsc_reports", flight.reports.adsc_manager.adsc_to_dict(), room=sid)
            flight.reports.adsc_manager.start_adsc_timer()
            self.socket_service.start_background_task(asyncio.run, flight.routine.simulate_flight_progress())
        else:
            self.socket_service.send("logon_failure", data={}, room=sid)

    @handle_errors(event_name="error", message="Failed to add log")
    def on_add_log(self, entry: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            new_log = flight.logs.add_log(entry.get("request"))
            self.socket_service.send("log_added", new_log.to_dict(), room=sid)
        else:
            print(f"Flight session not found for sid {sid}")

    @handle_errors(event_name="error", message="Failed to check if log is loadable")
    def on_change_status(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            log_id = data.get("logId")
            log = flight.logs.get_log_by_id(log_id)
            log.change_status_for_UM(data.get("status"))
            self.socket_service.send("status_changed", log.to_dict(), room=sid)

    def on_is_loadable(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            log = flight.logs.get_log_by_id(data.get("logId"))
            is_lodable = log.is_loadable()
            self.socket_service.send("message_loadable", is_lodable, room=sid)
        else:
            print(f"Flight session not found for sid {sid}")

    @handle_errors(event_name="error", message="Failed to load message")
    def on_load_fms(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            log = flight.logs.get_log_by_id(data.get("logId"))
            if log:
                waypoint = log.get_waypoint()
                new_route = flight.temp_route(waypoint)
                self.socket_service.send("new_route", new_route, room=sid)
            else:
                print(f"Log not found for sid {sid}")

    @handle_errors(event_name="error", message="Failed to load FMS route")
    def on_execute_route(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        new_route = flight.load_route(data.get("new_route", []))
        #flight.routine.update_routine(new_route)
        self.socket_service.send("route_loaded", new_route, room=sid)

    # START - actions for the routine 
    @handle_errors(event_name="error", message="Failed to play routine")
    def on_routine_play(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            flight.routine.play()

    @handle_errors(event_name="error", message="Failed to pause routine")
    def on_routine_pause(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            flight.routine.pause()

    @handle_errors(event_name="error", message="Failed to step back")
    def on_routine_step_back(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            flight.routine.step_back()

    def on_routine_step_forward(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            flight.routine.step_forward()

    @handle_errors(event_name="error", message="Failed to set speed")
    def on_routine_set_speed(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            speed_label = data.get("speed", "MEDIUM")
            selected_speed = Speed[speed_label]
            flight.routine.pause()
            flight.routine.simulation_speed(selected_speed)
            flight.routine.play()
    # END - actions for the routine

    # START - Report events
    # position report
    @handle_errors(event_name="error", message="Failed to send position report")
    def on_send_position_report(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            position_report = PositionReport(**data)
            flight.position_reports.append(position_report)
            self.socket_service.send("position_report_sent", position_report.to_dict(), room=sid)
    
    @handle_errors(event_name="error", message="Failed to get activate adsc emergency")

    # END - Report events

    @handle_errors(event_name="error", message="Failed to disconnect session")
    def on_disconnect(self, sid: str):
        sid = request.sid
        self.flight_manager.remove_session_by_sid(sid)
        # flight = self.flight_manager.get_session(sid)
        # flight.routine.reset_parameters()
        # flight.reports.position_reports = []
