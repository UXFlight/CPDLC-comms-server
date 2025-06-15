
class LogsManager:
    def __init__(self):
        self.logs = []

    def add_log(self, entry):
        self.logs.append(entry)

    def get_logs(self):
        return [log.to_dict() for log in self.logs]

    def to_dict(self):
        return self.get_logs()