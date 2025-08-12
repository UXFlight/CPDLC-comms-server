import asyncio
from app.classes.flight_session.flight_session import FlightSession

class FlightManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, routine, pilot_id, mongodb, socket, atc_id=None):
        if pilot_id not in self.sessions:
            session = FlightSession(routine, pilot_id, atc_id, mongodb, socket)
            self.sessions[pilot_id] = session
            return session
        return self.sessions[pilot_id]

    def get_session(self, pilot_id):
        return self.sessions.get(pilot_id)


    def remove_session_by_sid(self, pilot_id: str) -> bool:
        session: FlightSession | None = self.sessions.get(pilot_id)
        if session is None:
            print(f"No session found for pilot {pilot_id}")
            return False

        print(f"sessions before removal {self.sessions.keys()}")

        try:
            asyncio.run(session.routine.stop_and_wait(timeout=2.0))
        except Exception as e:
            print(f"Error while stopping routine for {pilot_id}: {e}")
        finally:
            # Supprimer après l’arrêt
            self.sessions.pop(pilot_id, None)
            print(f"sessions after removal {self.sessions.keys()}")
            print(f"Removed session for pilot {pilot_id}")

        return True

