class LogEntry:
    def __init__(self, content, direction, status, timestamp, sender):
        self.content = content
        self.direction = direction  # "UPLINK" or "DOWNLINK"
        self.status = status        # "SENT", "RECEIVED", etc.
        self.timestamp = timestamp
        self.sender = sender

    def to_dict(self):
        return {
            "content": self.content,
            "direction": self.direction,
            "status": self.status,
            "timestamp": self.timestamp,
            "sender": self.sender
        }

