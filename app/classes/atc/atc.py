class Atc:
    def __init__(self, name):
        self.name = name
        self.is_connected = False

    def connect(self):
        self.is_connected = True

    def disconnect(self):
        self.is_connected = False

    def to_dict(self):
        return {
            "name": self.name,
            "connected": self.is_connected
        }
