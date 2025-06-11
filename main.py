from flask import Flask # type: ignore
from app.classes import Socket
from flask_socketio import SocketIO # type: ignore
from app.controllers.routes import general_bp
from app.gateway.socket_gateway import SocketGateway
from app.managers.pilot_manager import PilotManager
#! from app.classes.ingsvc.agent import Echo

def create_app():
    app = Flask(__name__)
    app.register_blueprint(general_bp)
    socketio = SocketIO(app, cors_allowed_origins="*")
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    #! Echo.start_ingescape_agent()

    socket_service = Socket(socketio)
    pilot_manager = PilotManager() # keep tracks of connected pilots
    socket_manager = SocketGateway(socket_service, pilot_manager) # gateway for sockets

    socket_manager.init_events() # inits socket events

    socketio.run(app, host="0.0.0.0", port=5321)