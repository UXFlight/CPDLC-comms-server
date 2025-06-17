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
        #self.socket_service.listen('disconnect', self.on_disconnect)

    # === CONNECT EVENTS === #
    def on_connect(self, auth=None):
        sid = request.sid
        print("Client connected", sid)
        #self.socket_service.send("connected_ack", {"sid": sid})
    
    # def on_connect(self, auth=None):
    #     sid = request.sid
    #     name = request.name
    #     self.pilot_manager.create_pilot(sid, name)
    #     # more stuff later

    def sucessfull_connection(self, atc_id: str):
        flight = self.flight_manager.create_session(   
            flight_id=flight_plan["flight_id"],
            departure=flight_plan["departure"],
            arrival=flight_plan["arrival"],
            pilot_id=request.sid,
            atc_id=atc_id
        )
        print(f"Flight session created for {flight.pilot.name} with ATC {flight.atc.name}")
        self.socket_service.send("flight_details", flight.to_dict())
        self.socket_service.send("new_log", flight.logs.get_logs())

    # === DISCONNECT EVENTS === #
    # def on_disconnect(self, sid: str):
    #     sid = request.sid
    #     self.pilot_manager.remove_pilot(sid)
    #     # more stuff later

    