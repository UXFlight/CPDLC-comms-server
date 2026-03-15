from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask # type: ignore
from app.classes import Socket
from flask_socketio import SocketIO # type: ignore
from app.controllers.routes import general_bp
from app.classes.logging import get_logger
from app.gateway.socket_gateway import SocketGateway
from flask_cors import CORS # type: ignore
from app.managers.flight_manager.flight_manager import FlightManager
# from app.classes.ingsvc.agent import Echo

port = int(os.environ.get('PORT', 5321))
debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
socket_log_output = os.getenv("SOCKET_LOG_OUTPUT", "false").lower() == "true"

allowed_origins = [
    "http://localhost:3000",
    "http://155.138.147.86",
    "http://mycpdlc.com"
]

def create_app():
    app = Flask(__name__)
    CORS(app, origins=allowed_origins)
    app.register_blueprint(general_bp)
    socketio = SocketIO(
        app,
        cors_allowed_origins=allowed_origins,
        async_mode='eventlet',
        logger=socket_log_output,
        engineio_logger=socket_log_output,
    )
    return app, socketio

app, socketio = create_app()
socket_service = Socket(socketio)
flight_manager = FlightManager()
socket_manager = SocketGateway(socket_service, flight_manager)
socket_manager.init_events()

@app.route('/')
def index():
    return 'Welcome !'

if __name__ == '__main__':
    # Echo.start_ingescape_agent()
    logger = get_logger()
    logger.info(
        "server_startup",
        extra={
            "client_id": "-",
            "event": "startup",
            "meta": (
                f" | host=0.0.0.0"
                f" | port={port}"
                f" | debug={debug_mode}"
                f" | socket_log_output={socket_log_output}"
            ),
        },
    )
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode,
        log_output=socket_log_output,
    )
