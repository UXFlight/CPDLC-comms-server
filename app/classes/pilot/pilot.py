class Pilot:
    def __init__(self, id):
        self.id = id
        self.is_connected = False

    def connect(self):
        self.is_connected = True

    def disconnect(self):
        self.is_connected = False

    def to_dict(self):
        return {
            "id": self.id,
            "connected": self.is_connected
        }
