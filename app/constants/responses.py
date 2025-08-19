
from dataclasses import dataclass


DM27 = {
    "direct_response":{
      "ref": "UM82",
      "content": "CLEARED TO DEVIATE UP TO 20NM LEFT OF ROUTE",
      "direction": "UPLINK",
      "status": "NEW",
      "timestamp": "2025-06-15T14:31:00Z",
      "sender": "Controller",
      "intent": "Clearance for the aircraft to deviate from the cleared route up to 20 nautical miles to the left."
    },
    "delayed_response": {
      "ref": "UM127",
      "content": "REPORT BACK ON ROUTE",
      "direction": "UPLINK",
      "status": "NEW",
      "timestamp": "2025-06-15T14:31:30Z",
      "sender": "Controller",
      "intent": "Instruction to report when the aircraft is back on the cleared route."
    }
}

PREDEFINED_RESPONSES = [DM27]

REPORT_INITIATION = ["UM127", "UM128", "UM129", "UM130", "UM131", "UM132", "UM133", "UM134", "UM135", "UM136", "UM137", "UM138", "UM139", "UM140", "UM141", "UM142", "UM143", "UM145", "UM146", "UM147", "UM120", "UM121", "UM122"]

# INDEX REPORT
AUTOMATIC_INDEX_REPORT = ["UM127", "UM128", "UM129", "UM130", "UM134",]

# POSITION REPORT
POSITION_REPORT_REQUEST = ["UM147"]

# ADS-C REPORT
ADS_C_REPORT_REQUEST = []
ADSC_EMERGENCY = 'UM169ak' #confirm adsc emergency
ADSC_CONFIRM = 'UM169an' #confirm adsc armed
ADSC_DEVIATION = ['UM169f', 'UM169t', 'UM169v'] #route, level, speed
ADSC_SHUT_DOWN = ['UM169ao', 'UM169at']

ADS_C_EMERGENCY_THREAD = [ADSC_EMERGENCY, "DM0", "DM67ab"]

@dataclass
class ResponseHandler:
    initiator: str
    response: str
    second_response: str
    third_response: str

# MONITORING_REPORT
MONITORING_REPORT_REQUEST = ["UM120", "UM121", "UM122"]

# EMERGENCY_REPORT
EMERGENCY_REPORT_REQUEST = ["DM55", "DM56"]