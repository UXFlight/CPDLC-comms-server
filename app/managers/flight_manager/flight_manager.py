from app.classes.flight_session.flight_session import FlightSession


class FlightManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, flight_id, departure, arrival, pilot_id, atc_id):
        if flight_id not in self.sessions:
            session = FlightSession(flight_id, departure, arrival, pilot_id, atc_id)
            self.sessions[flight_id] = session
            return session
        return self.sessions[flight_id]

    def get_session(self, flight_id):
        return self.sessions.get(flight_id)

    def remove_session(self, flight_id):
        if flight_id in self.sessions:
            del self.sessions[flight_id]

