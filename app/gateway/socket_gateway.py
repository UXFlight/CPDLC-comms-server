import asyncio
from copy import deepcopy
from flask import request  # type: ignore
from app.classes import Socket  # type: ignore
from app.database.mongo_db import MongoDb
from app.managers.flight_manager.flight_manager import FlightManager
from app.database.flight_plan.flight_plan import flight_plan
from app.utils.error_handler import handle_errors


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
        self.socket_service.listen('disconnect', self.on_disconnect)

    @handle_errors(event_name="error", message="Failed to create flight session")
    def on_connect(self, auth=None):
        sid = request.sid
        plan = deepcopy(flight_plan)
        plan["flight_id"] = f"{plan['flight_id']}"
        flight = self.flight_manager.create_session(
            flight_id=plan["flight_id"],
            departure=plan["departure"],
            arrival=plan["arrival"],
            pilot_id=sid,
            route=plan["route"],
            mongodb=self.mongodb,
            socket=self.socket_service,
            room=sid
        )
        self.socket_service.send("connected", flight.to_dict(), room=sid)
        self.socket_service.start_background_task(asyncio.run, flight.routine.simulate_flight_progress())

    @handle_errors(event_name="error", message="Failed to logon atc")
    def on_logon(self, data: dict):
        sid = request.sid
        atc_available = self.mongodb.find_available_atc(data.get("username"))
        print(f"ATC available: {atc_available}")
        if atc_available:
            flight = self.flight_manager.get_session_by_pilot(sid)
            flight.atc_id = data.get("username")
            self.socket_service.send("logon_success", data={}, room=sid)
            self.socket_service.send("load_logs", flight.logs.get_logs(), room=sid)
        else:
            self.socket_service.send("logon_failure", data={}, room=sid)

    @handle_errors(event_name="error", message="Failed to add log")
    def on_add_log(self, entry: dict):
        sid = request.sid
        flight = self.flight_manager.get_session_by_pilot(sid)
        if flight:
            new_log = flight.logs.add_log(entry.get("request"))
            self.socket_service.send("log_added", new_log.to_dict(), room=sid)
        else:
            print(f"Flight session not found for sid {sid}")

    @handle_errors(event_name="error", message="Failed to check if log is loadable")
    def on_change_status(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session_by_pilot(sid)
        if flight:
            log_id = data.get("logId")
            log = flight.logs.get_log_by_id(log_id)
            log.change_status_for_UM(data.get("status"))
            self.socket_service.send("status_changed", log.to_dict(), room=sid)

    @handle_errors(event_name="error", message="Failed to check if log is loadable")
    def on_is_loadable(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session_by_pilot(sid)
        if flight:
            log = flight.logs.get_log_by_id(data.get("logId"))
            is_lodable = log.is_loadable()
            self.socket_service.send("message_loadable", is_lodable, room=sid)
        else:
            print(f"Flight session not found for sid {sid}")

    @handle_errors(event_name="error", message="Failed to load message")
    def on_load_fms(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session_by_pilot(sid)
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
        flight = self.flight_manager.get_session_by_pilot(sid)
        new_route = flight.load_route(data.get("new_route", []))
        self.socket_service.send("route_loaded", new_route, room=sid)

    @handle_errors(event_name="error", message="Failed to disconnect session")
    def on_disconnect(self, sid: str):
        sid = request.sid
        self.flight_manager.remove_session_by_pilot(sid)
