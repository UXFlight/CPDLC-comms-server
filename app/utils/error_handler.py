from flask import request # type: ignore
from app.core.logging import log_error

def handle_errors(event_name="error", message="An error occurred"):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            sid = request.sid
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                log_error(
                    client_id=sid,
                    event=f"{func.__name__}_failed",
                    error=e,
                    handler=func.__name__,
                )
                self.socket_service.send(event_name, {"message": message}, room=sid)
        return wrapper
    return decorator
