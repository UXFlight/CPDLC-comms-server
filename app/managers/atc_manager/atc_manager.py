from app.classes import Pilot
from app.classes.atc import atc

class AtcManager:

    def __init__(self):
        self.atcs = {}

    def create_pilot(self, atc_sid, atc_name):
        if atc_sid not in self.atcs:
            self.atcs[atc_sid] = atc(atc_sid, atc_name)
        else:
            raise ValueError(f"Pilot with ID {atc_sid} already exists.")

    def get_pilots(self):
        return self.atcs
    
    def remove_pilot(self, atc_sid):
        if atc_sid in self.atcs:
            del self.atcs[atc_sid]