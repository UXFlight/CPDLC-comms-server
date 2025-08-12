
class ADSCContract:
    def __init__(self, contract_id: str, center: str, period: str):
        self.id = contract_id
        self.center = center
        self.period = period
        self.time_Next = 0
        self.is_active = True