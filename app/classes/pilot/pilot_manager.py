class PilotManager:
    def __init__(self):
        self.pilots = {}

    def get_pilot(self, sid):
        if self.pilots.get(sid) is None:
            raise ValueError(f"Pilot with sid {sid} not found.")
        return self.pilots[sid] # !!!!!