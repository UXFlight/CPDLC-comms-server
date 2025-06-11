from app.classes import Pilot

class PilotManager:

    def __init__(self):
        self.pilots = {}

    def create_pilot(self, pilot_sid, pilot_name):
        if pilot_sid not in self.pilots:
            self.pilots[pilot_sid] = Pilot(pilot_sid, pilot_name)
        else:
            raise ValueError(f"Pilot with ID {pilot_sid} already exists.")

    def get_pilots(self):
        return self.pilots
    
    def remove_pilot(self, pilot_sid):
        if pilot_sid in self.pilots:
            del self.pilots[pilot_sid]