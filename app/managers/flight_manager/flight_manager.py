import asyncio
from app.classes.flight_session.flight_session import FlightSession
from app.classes.logging import log_error, log_user_action

class FlightManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, routine, pilot_id, mongodb, socket, atc_id=None):
        if pilot_id not in self.sessions:
            session = FlightSession(routine, pilot_id, atc_id, mongodb, socket)
            self.sessions[pilot_id] = session
            log_user_action(pilot_id, "session_create")
            return session
        return self.sessions[pilot_id]

    def get_session(self, pilot_id):
        return self.sessions.get(pilot_id)


    def remove_session_by_sid(self, pilot_id: str) -> bool:
        session: FlightSession | None = self.sessions.get(pilot_id)
        if session is None:
            log_error(
                client_id=pilot_id,
                event="session_remove_failed",
                error="session_not_found",
            )
            return False
        asyncio.run(session.reports.adsc_manager.stop_adsc_and_wait(timeout=2.0))

        try:
            asyncio.run(session.routine.stop_and_wait(timeout=2.0))
        except Exception as e:
            log_error(client_id=pilot_id, event="routine_stop_failed", error=e)
        finally:
            completion_pct = session.route_completion_pct()
            session_duration = session.session_duration_sec()
            log_user_action(
                pilot_id,
                "route_session_closed",
                departure=session.departure,
                arrival=session.arrival,
                route_completion_pct=completion_pct,
                session_duration_sec=session_duration,
            )
            # Supprimer après l’arrêt
            self.sessions.pop(pilot_id, None)
            log_user_action(pilot_id, "session_remove")

        return True
