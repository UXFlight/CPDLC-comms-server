from enum import Enum
import re
from typing import Any, Dict
import uuid
from app.utils.time_utils import get_current_timestamp

ACTION_REQUIRED_UM = ["Y", "W/U", "A/N", "R"]
NO_ACTION_REQUIRED_UM = ["N", "N/E"]

class LogEntry:
    def __init__(self, ref, content, direction, status, urgency, response_required, intent=None, position=None, additional=None, mongodb=None, communication_thread=None, acceptable_responses=None, id=None, timestamp=None):
        self.id = str(uuid.uuid4()) if id is None else id
        self.ref = ref
        self.content = content
        self.direction = direction
        self.status = status
        self.urgency = urgency
        self.timestamp = timestamp if timestamp is not None else get_current_timestamp()
        self.intent = intent
        self.position = position
        self.additional = additional if additional is not None else []
        self.__mongodb = mongodb
        self.communication_thread = communication_thread if communication_thread is not None else []
        self.response_required = response_required
        self.acceptable_responses = acceptable_responses if acceptable_responses is not None else []
        #self.category = None


    def to_dict(self, depth=0, max_depth=5):
        if depth > max_depth:
            return {"id": self.id, "ref": self.ref, "note": "Max depth reached"}

        return {
            "id": self.id,
            "ref": self.ref,
            "direction": self.direction,
            "element": self.content,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "urgency": self.urgency,
            "intent": self.intent,
            "timeStamp": self.timestamp,
            "additional": self.additional,
            "communication_thread": [
                entry.to_dict(depth=depth+1, max_depth=max_depth)
                for entry in self.communication_thread
            ],
            "response_required": self.response_required,
            "acceptable_responses": self.acceptable_responses,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], mongodb=None) -> "LogEntry":
        return cls(
            ref=data.get("ref"),
            content=data.get("element"),  
            direction=data.get("direction", "uplink"),
            status=data.get("status", "new"),
            intent=data.get("intent"),
            additional=data.get("additional", []),
            urgency=data.get("urgency", "normal"),
            mongodb=mongodb,
            response_required=data.get("response_required", False),
            acceptable_responses=data.get("acceptable_responses", []),
            id=data.get("id"),
        )

    def is_loadable(self):
        ref = self.__mongodb.find_UM_by_ref(self.ref)
        if not ref:
            print(f"No UM found for ref {self.ref}")
            return False

        category = ref.get("Category", "")
        return "Route Modifications" in category

    def get_waypoint(self):
        um_ref = self.__mongodb.find_datalink_by_ref(self.ref)
        template = um_ref.get("Message_Element")
        message = self.content

        regex_pattern = re.escape(template)
        regex_pattern = regex_pattern.replace(r'\[position\]', r'(?P<position>\w+)')

        match = re.match(regex_pattern, message)
        if match:
            return match.group("position")
        return None
    
    def change_status_for_UM(self, ref):
        if ref == "DM0":
            self.status = "ACCEPTED"
        elif ref == "DM1":
            self.status = "REJECTED"
        elif ref == "DM2":
            self.status = "OPENED"
        else :
            self.status = "ACCEPTED"
            return
        self.format_simple_response(ref)    
        return self
    
    # def get_available_actions(self):
    #     if self.response_required:
    #         if len(self.acceptable_responses) > 0:
    #             return "datalinks"
    #         else:
    #             return "basic"
    #     else :
    #         return "no_actions"

    @staticmethod
    def is_response_required(datalink) -> bool:
        response_required = datalink.get("Response_required", "")
        return response_required[0] in ACTION_REQUIRED_UM

    @staticmethod
    def formatted_message(request_data: dict, mongodb) -> str:
        message_ref = request_data.get("messageRef")
        arguments = request_data.get("arguments", [])
        position_arg = request_data.get("positionSelected", None)
        time_arg = request_data.get("timeSelected", None)

        if isinstance(time_arg, dict):
            hh = time_arg.get("hh", "").zfill(2)
            mm = time_arg.get("mm", "").zfill(2)
            time_arg = f"{hh}:{mm}"

        d_message = mongodb.find_datalink_by_ref(message_ref)
        if not d_message:
            return ""

        result = d_message.get("Message_Element", "")
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
