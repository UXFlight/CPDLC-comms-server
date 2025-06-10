from flask import request

class SocketGateway:
    def __init__(self, socket_service, pilot_manager=None):
        self.socket_service = socket_service
        self.pilot_manager = pilot_manager

    def init_events(self):
        pass