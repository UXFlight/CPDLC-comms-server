class Pilot:
    def __init__(self, name: str, sid: str):
        self.name = name
        self.sid = sid

    def fly(self):
        return f"{self.name} is flying the aircraft."

    def get_details(self):
        return f"Pilot Name: {self.name}, Age: {self.age}, Experience: {self.experience_years} years"