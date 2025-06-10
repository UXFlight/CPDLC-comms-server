from flask import Flask # type: ignore
from flask_socketio import SocketIO # type: ignore
from app.gateway.socket_gateway import SocketGateway
from app.classes import Socket
from app.controllers.routes import general_bp
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
    socket_manager = SocketGateway(socket_service, )

    socket_manager.init_events()

    socketio.run(app, host="0.0.0.0", port=5321)