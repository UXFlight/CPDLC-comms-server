import asyncio
from copy import deepcopy
from enum import Enum
from flask import json, request  # type: ignore
from app.classes import Socket  # type: ignore
from app.classes.flight_session.flight_session import FlightSession
from app.classes.log_entry.log_entry import LogEntry
from app.classes.report.position_report import PositionReport
from app.database.mongo_db import MongoDb
from app.managers.flight_manager.flight_manager import FlightManager
from app.database.flight_plan.flight_plan import flight_plan
from app.database.flight_plan.routine import routine
from app.managers.logs_manager.logs_manager import LogsManager
from app.utils.error_handler import handle_errors

class Speed(Enum):
    SLOW = 30
    MEDIUM = 60
    FAST = 100
    EXTREME = 200

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
        self.socket_service.listen('cancel_execute_route', self.on_cancel_execute_route)
        self.socket_service.listen('routine_play', self.on_routine_play)
        self.socket_service.listen('routine_pause', self.on_routine_pause)
        self.socket_service.listen('routine_step_back', self.on_routine_step_back)
        self.socket_service.listen('routine_step_forward', self.on_routine_step_forward)
        self.socket_service.listen('routine_set_speed', self.on_routine_set_speed)
        self.socket_service.listen('ads_c_emergency_on', self.on_activate_adsc_emergency)
        self.socket_service.listen('ads_c_emergency_off', self.on_deactivate_adsc_emergency)
        self.socket_service.listen('ads_c_disabled', self.on_disable_adsc)
        self.socket_service.listen('ads_c_enable', self.on_enable_adsc)
        self.socket_service.listen('pilot_response', self.on_pilot_response)
        self.socket_service.listen('disconnect', self.on_disconnect)

    def on_connect(self, auth=None):
        sid = request.sid
        flight = self.flight_manager.create_session(routine, sid, self.mongodb, self.socket_service)
        self.socket_service.send("connected", flight.to_dict(), room=sid)

    def on_logon(self, data: dict):
        sid = request.sid
        atc_available = self.mongodb.find_available_atc(data.get("username"))
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

    def on_add_log(self, payload: dict):
        sid = request.sid
        entry = payload.get("log_entry") or {}
        thread_id = payload.get("thread_id") or ""
        flight = self.flight_manager.get_session(sid)
        if not flight or not entry:
            return
        if thread_id:
            log = LogEntry.from_dict(entry, mongodb=flight.logs._mongodb)
            new_log = flight.logs.add_log(log, thread_id=thread_id)   
        else:
            new_log = flight.logs.create_add_log(entry)             
        self.socket_service.send("log_added", new_log.to_dict(), room=sid)

    # START -  PILOT RESPONSE
    def on_pilot_response(self, data: dict):
        sid = request.sid
        entry = data.get("log_entry")
        thread_id = data.get("thread_id", "")
        flight : FlightSession = self.flight_manager.get_session(sid)
        if flight:
            log = LogsManager.create_log(self.mongodb, entry.get("ref"), entry.get("text"))
            new_log = flight.logs.add_log(log, thread_id=thread_id)
            self.socket_service.send("log_added", new_log.to_dict(), room=sid)
            parent = flight.logs.get_parent_by_child_id(thread_id)
            scenario = flight.scenarios.on_pilot_dm_by_thread(
                        thread_id=parent.id,
                        pilot_ref=entry.get("ref"),
                        pilot_text=entry.get("text")
            )
            print(f"scenario {scenario}")
    
    @handle_errors(event_name="error", message="Failed to check if log is loadable")
    def on_change_status(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            log_id = data.get("logId")
            log: LogEntry = flight.logs.get_log_by_id(log_id)
            log.change_status_for_UM(data.get("status"))
            self.socket_service.send("status_changed", log.to_dict(), room=sid)

    # END - PILOT RESPONSE

    def on_is_loadable(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            log = flight.logs.get_log_by_id(data.get("logId"))
            is_lodable = log.is_loadable()
            self.socket_service.send("message_loadable", is_lodable, room=sid)
        else:
            print(f"Flight session not found for sid {sid}")

    def on_load_fms(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            log = flight.logs.get_log_by_id(data.get("logId"))
            if log:
                flight.routine.pause()
                waypoint = log.get_waypoint()
                current_waypoint = flight.routine.current_fix
                new_route = flight.temp_route(current_waypoint, waypoint)
                self.socket_service.send("new_route", new_route, room=sid)
            else:
                print(f"Log not found for sid {sid}")

    @handle_errors(event_name="error", message="Failed to load FMS route")
    def on_execute_route(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight: 
            new_route = flight.load_route(data.get("new_route", []))
            flight.routine.set_new_route(new_route)
        self.socket_service.send("route_loaded", new_route, room=sid)

    def on_cancel_execute_route(self):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        if flight:
            flight.routine.play()

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
    

    # adsc events
    def on_activate_adsc_emergency(self):
        sid = request.sid
        flight : FlightSession = self.flight_manager.get_session(sid)
        if flight:
            flight.reports.adsc_manager.activate_emergency()

    @handle_errors(event_name="error", message="Failed to deactivate adsc emergency")
    def on_deactivate_adsc_emergency(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        # if flight:
        #     flight.adsc_manager.deactivate_emergency()

    @handle_errors(event_name="error", message="Failed to disable adsc")
    def on_disable_adsc(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        #if flight:
            #flight.adsc_manager.disable()
    
    @handle_errors(event_name="error", message="Failed to enable adsc")
    def on_enable_adsc(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session(sid)
        #if flight:
            #flight.adsc_manager.enable()

    # END - Report events

    @handle_errors(event_name="error", message="Failed to disconnect session")
    def on_disconnect(self, sid: str):
        sid = request.sid
        self.flight_manager.remove_session_by_sid(sid)