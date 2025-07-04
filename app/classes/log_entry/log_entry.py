import re
import uuid
from app.database.uplinks import uplinks
from app.database.downlinks import downlinks
from app.utils.time_utils import get_current_timestamp

class LogEntry:
    def __init__(self, ref, content, direction, status, intent=None, position=None, additional=[]):
        self.id = str(uuid.uuid4())  
        self.ref = ref
        self.content = content
        self.direction = direction
        self.status = status
        self.timestamp = get_current_timestamp()
        self.intent = intent
        self.position = position
        self.additional = additional

    def to_dict(self):
        return {
            "id": self.id,
            "ref": self.ref,
            "direction": self.direction,
            "element": self.content,
            "status": self.status,
            "intent": self.intent,
            "timeStamp": self.timestamp,
            "additional": self.additional
        }

    def is_loadable(self):
        um_ref = LogEntry.find_UM_by_ref(self.ref)
        print(f"Checking if UM exists for ref {self.ref}: {um_ref}")
        if not um_ref:
            print(f"No UM found for ref {self.ref}")
            return False

        category = um_ref.get("Category", "")
        return "Route Modifications" in category

        # return self.status in ["open", "new"]


    def get_waypoint(self):
        um_ref = LogEntry.find_UM_by_ref(self.ref)
        if not um_ref:
            return None

        template = um_ref.get("Message_Element")
        message = self.content

        regex_pattern = re.escape(template)
        regex_pattern = regex_pattern.replace(r'\[position\]', r'(?P<position>\w+)')

        match = re.match(regex_pattern, message)
        if match:
            return match.group("position")
        return None

    @staticmethod
    def find_DM_by_ref(ref):
        return next(
            (msg for msg in downlinks if msg.get("Ref_Num", "").replace(" ", "") == ref),
            None
        )
    
    @staticmethod
    def find_UM_by_ref(ref):
        return next(
            (msg for msg in uplinks if msg.get("Ref_Num", "").replace(" ", "") == ref),
            None
        )
        

    @staticmethod
    def formatted_message(request_data: dict) -> str:
        import re

        message_ref = request_data.get("messageRef")
        arguments = request_data.get("arguments", [])
        position_arg = request_data.get("positionSelected", None)
        time_arg = request_data.get("timeSelected", None)

        if isinstance(time_arg, dict):
            hh = time_arg.get("hh", "").zfill(2)
            mm = time_arg.get("mm", "").zfill(2)
            time_arg = f"{hh}:{mm}"

        d_message = LogEntry.find_DM_by_ref(message_ref)
        print(f"Looking for DM with ref {message_ref}: {d_message}")
        if not d_message:
            return ""

        result = d_message.get("Message_Element", "")
        print(f"Message Element found: {result}")
        arg_index = 0

        def replacer(match):
            nonlocal arg_index
            keyword = match.group(0).lower()

            if "[position]" in keyword and position_arg:
                return position_arg
            elif "[time]" in keyword and time_arg:
                return time_arg
            elif arg_index < len(arguments):
                value = arguments[arg_index]
                arg_index += 1
                return value
            return "[missing]"

        formatted = re.sub(r"\[.*?\]", replacer, result)
        return formatted.strip()
