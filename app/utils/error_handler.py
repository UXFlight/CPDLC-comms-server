from flask import request # type: ignore

def handle_errors(event_name="error", message="An error occurred"):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            sid = request.sid
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                print(f"Error in {func.__name__} for sid {sid}: {e}")
                self.socket_service.send(event_name, {"message": message}, room=sid)
        return wrapper
    return decorator
