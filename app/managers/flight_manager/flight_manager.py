from app.classes.flight_session.flight_session import FlightSession


class FlightManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, flight_id, departure, arrival, pilot_id, route, mongodb, socket, room, atc_id=None):
        if flight_id not in self.sessions:
            session = FlightSession(flight_id, departure, arrival, pilot_id, route, atc_id, mongodb, socket, room)
            self.sessions[flight_id] = session
            return session
        return self.sessions[flight_id]

    def get_session(self, flight_id):
        return self.sessions.get(flight_id)
    
    def get_session_by_pilot(self, pilot_id):
        for session in self.sessions.values():
            if session.pilot.id == pilot_id:
                return session
        return None

    def remove_session(self, flight_id):
        if flight_id in self.sessions:
            del self.sessions[flight_id]

    def remove_session_by_pilot(self, pilot_id):
        for flight_id, session in list(self.sessions.items()):
            if session.pilot.id == pilot_id:
                del self.sessions[flight_id]
                print(f"Removed session for pilot {pilot_id}")
                return True
        print(f"No session found for pilot {pilot_id}")
        return False
