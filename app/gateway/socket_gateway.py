from flask import request # type: ignore
from app.classes import Socket # type: ignore
from app.managers.pilot_manager import PilotManager

class SocketGateway:
    def __init__(self, socket_service: Socket, pilot_manager: PilotManager):
        self.socket_service = socket_service
        self.pilot_manager = pilot_manager

    def init_events(self):
        self.socket_service.listen('connect', self.on_connect)
        self.socket_service.listen('disconnect', self.on_disconnect)

    # === CONNECT EVENTS === #
    def on_connect(self, auth=None):
        sid = request.sid
        name = request.name
        self.pilot_manager.create_pilot(sid, name)
        # more stuff later

    # === DISCONNECT EVENTS === #
    def on_disconnect(self, sid: str):
        sid = request.sid
        self.pilot_manager.remove_pilot(sid)
        # more stuff later

    