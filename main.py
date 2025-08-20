import os
from flask import Flask  # type: ignore
from app.classes import Socket
from flask_socketio import SocketIO  # type: ignore
from app.controllers.routes import general_bp
from app.database.mongo_db import MongoDb
from app.gateway.socket_gateway import SocketGateway
from flask_cors import CORS # type: ignore
from app.managers.flight_manager.flight_manager import FlightManager
# from app.classes.ingsvc.agent import Echo

port = int(os.environ.get('PORT', 5321))

allowed_origins = [
    "http://localhost:3000",
    "https://mycpdlc.netlify.app",
]

def create_app():
    app = Flask(__name__)
    CORS(app, origins=allowed_origins)
    app.register_blueprint(general_bp)
    
    socketio = SocketIO(
        app, 
        cors_allowed_origins=allowed_origins,
        logger=True,
        engineio_logger=True
    )
    return app, socketio

app, socketio = create_app()

socket_service = Socket(socketio)
flight_manager = FlightManager()
mongodb = MongoDb()
socket_manager = SocketGateway(socket_service, flight_manager, mongodb)
socket_manager.init_events()

@app.route('/')
def index():
    return 'Welcome !'

if __name__ == '__main__':
    # Echo.start_ingescape_agent()
    socketio.run(app, host="0.0.0.0", port=port, debug=False)