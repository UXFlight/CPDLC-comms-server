from copy import deepcopy
from flask import request # type: ignore
from app.classes import Socket # type: ignore
from app.managers.flight_manager.flight_manager import FlightManager
from app.database.flight_plan import flight_plan

class SocketGateway:
    def __init__(self, socket_service: Socket, flight_manager: FlightManager):
        self.socket_service = socket_service
        self.flight_manager = flight_manager

    def init_events(self):
        self.socket_service.listen('connect', self.on_connect)
        self.socket_service.listen('sucessfull_connection', self.sucessfull_connection)
        self.socket_service.listen('add_log', self.on_add_log)
        self.socket_service.listen('change_status', self.on_change_status)
        self.socket_service.listen('disconnect', self.on_disconnect)

    def on_connect(self, auth=None):
        sid = request.sid
        print("Client connected", sid)

    def sucessfull_connection(self, atc_id: str):
        sid = request.sid
        plan = deepcopy(flight_plan)

        plan["flight_id"] = f"{plan['flight_id']}"
        flight = self.flight_manager.create_session(
            flight_id=plan["flight_id"],
            departure=plan["departure"],
            arrival=plan["arrival"],
            pilot_id=sid,
            route=plan["route"],
            atc_id=atc_id
        )
        self.socket_service.send("flight_details", flight.to_dict(),  room=sid)
        self.socket_service.send("load_logs", flight.logs.get_logs(), room=sid)

    def on_add_log(self, entry: dict):
        sid = request.sid
        flight = self.flight_manager.get_session_by_pilot(sid)
        if flight:
            new_log = flight.logs.add_log(entry.get("request"))
            self.socket_service.send("log_added", new_log.to_dict(), room=sid)
        else:
            print(f"Flight session not found for sid {sid}")

    def on_change_status(self, data: dict):
        sid = request.sid
        flight = self.flight_manager.get_session_by_pilot(sid)
        if flight:
            log_id = data.get("logId")
            flight.logs.change_status(log_id, data.get("status"))

    def on_disconnect(self, sid: str):
        sid = request.sid
        self.flight_manager.remove_session_by_pilot(sid)

    