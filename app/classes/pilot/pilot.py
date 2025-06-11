

class Pilot:
    def __init__(self, sid: str, name: str):
        self.sid = sid
        self.name = name

    def fly(self):
        return f"{self.name} is flying the aircraft."

    def get_details(self):
        return f"Pilot Name: {self.name}, Socket-ID: {self.sid}"