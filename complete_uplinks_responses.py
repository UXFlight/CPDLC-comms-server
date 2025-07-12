#!/usr/bin/env python3
import json

# Path to the UpLinks.json file
file_path = r"c:\Users\irina\OneDrive\Desktop\CPDLC-comms-server\app\database\data\UpLinks.json"

# Mapping of DM codes to their text descriptions
dm_mapping = {
    "DM0": "WILCO",
    "DM1": "UNABLE",
    "DM2": "STANDBY",
    "DM3": "ROGER",
    "DM4": "AFFIRM",
    "DM5": "NEGATIVE",
    "DM6": "REQUEST [level]",
    "DM7": "REQUEST BLOCK [level] TO [level]",
    "DM8": "REQUEST CRUISE CLIMB TO [level]",
    "DM9": "REQUEST CLIMB TO [level]",
    "DM10": "REQUEST DESCENT TO [level]",
    "DM11": "AT [position] REQUEST CLIMB TO [level]",
    "DM12": "AT [position] REQUEST DESCENT TO [level]",
    "DM13": "AT [time] REQUEST CLIMB TO [level]",
    "DM14": "AT [time] REQUEST DESCENT TO [level]",
    "DM15": "REQUEST OFFSET [specified distance] [direction] OF ROUTE",
    "DM16": "AT [position] REQUEST OFFSET [specified distance] [direction] OF ROUTE",
    "DM17": "AT [time] REQUEST OFFSET [specified distance] [direction] OF ROUTE",
    "DM18": "REQUEST [speed]",
    "DM19": "REQUEST [speed] TO [speed]",
    "DM20": "REQUEST VOICE CONTACT",
    "DM21": "REQUEST VOICE CONTACT [frequency]",
    "DM22": "REQUEST DIRECT TO [position]",
    "DM23": "REQUEST [procedure name]",
    "DM24": "REQUEST CLEARANCE [route clearance]",
    "DM25": "REQUEST [clearance type] CLEARANCE",
    "DM26": "REQUEST WEATHER DEVIATION TO [position] VIA [route clearance]",
    "DM27": "REQUEST WEATHER DEVIATION UP TO [specified distance] [direction] OF ROUTE",
    "DM28": "LEAVING [level]",
    "DM29": "CLIMBING TO [level]",
    "DM30": "DESCENDING TO [level]",
    "DM31": "PASSING [position]",
    "DM32": "PRESENT LEVEL [level]",
    "DM33": "PRESENT POSITION [position]",
    "DM34": "PRESENT SPEED [speed]",
    "DM35": "PRESENT HEADING [degrees]",
    "DM36": "PRESENT GROUND TRACK [degrees]",
    "DM37": "MAINTAINING [level]",
    "DM38": "ASSIGNED LEVEL [level]",
    "DM39": "ASSIGNED SPEED [speed]",
    "DM40": "ASSIGNED ROUTE [route clearance]",
    "DM41": "BACK ON ROUTE",
    "DM42": "NEXT WAYPOINT [position]",
    "DM43": "NEXT WAYPOINT ETA [time]",
    "DM44": "ENSUING WAYPOINT [position]",
    "DM45": "REPORTED WAYPOINT [position]",
    "DM46": "REPORTED WAYPOINT [time]",
    "DM47": "SQUAWKING [code]",
    "DM48": "POSITION REPORT [position report]",
    "DM49": "WHEN CAN WE EXPECT [speed]",
    "DM50": "WHEN CAN WE EXPECT [speed] TO [speed]",
    "DM51": "WHEN CAN WE EXPECT BACK ON ROUTE",
    "DM52": "WHEN CAN WE EXPECT LOWER LEVEL",
    "DM53": "WHEN CAN WE EXPECT HIGHER LEVEL",
    "DM54": "WHEN CAN WE EXPECT CRUISE CLIMB TO [level]",
    "DM55": "PAN PAN PAN",
    "DM56": "MAYDAY MAYDAY MAYDAY",
    "DM57": "[remaining fuel] OF FUEL REMAINING AND [persons on board] PERSONS ON BOARD",
    "DM58": "CANCEL EMERGENCY",
    "DM59": "DIVERTING TO [position] VIA [route clearance]",
    "DM60": "OFFSETTING [specified distance] [direction] OF ROUTE",
    "DM61": "DESCENDING TO [level]",
    "DM62": "ERROR [error information]",
    "DM63": "NOT CURRENT DATA AUTHORITY",
    "DM64": "[facility designation]",
    "DM65": "DUE TO WEATHER",
    "DM66": "DUE TO AIRCRAFT PERFORMANCE",
    "DM67": "[free text]",
    "DM68": "[free text]",
    "DM69": "REQUEST VMC DESCENT",
    "DM70": "REQUEST HEADING [degrees]",
    "DM71": "REQUEST GROUND TRACK [degrees]",
    "DM72": "[version number]",
    "DM73": "[version number]",
    "DM74": "REQUEST TO MAINTAIN OWN SEPARATION AND VMC",
    "DM75": "AT PILOTS DISCRETION",
    "DM76": "REACHING BLOCK [level] TO [level]",
    "DM77": "ASSIGNED BLOCK [level] TO [level]",
    "DM78": "AT [time] [distance] [to/from] [position]",
    "DM79": "ATIS [atis code]",
    "DM80": "DEVIATING UP TO [specified distance] [direction] OF ROUTE",
    "DM81": "WE CAN ACCEPT [level] AT [time]",
    "DM82": "WE CANNOT ACCEPT [level]",
    "DM83": "WE CAN ACCEPT [speed] AT [time]",
    "DM84": "WE CANNOT ACCEPT [speed]",
    "DM85": "WE CAN ACCEPT [specified distance] [direction] AT [time]",
    "DM86": "WE CANNOT ACCEPT [specified distance] [direction]",
    "DM87": "WHEN CAN WE EXPECT CLIMB TO [level]",
    "DM88": "WHEN CAN WE EXPECT DESCENT TO [level]",
    "DM89": "MONITORING [unit name] [frequency]",
    "DM90": "[free text]",
    "DM91": "[free text]",
    "DM92": "[free text]",
    "DM93": "[free text]",
    "DM94": "[free text]",
    "DM95": "[free text]",
    "DM96": "[free text]",
    "DM97": "[free text]",
    "DM98": "[free text]",
    "DM99": "CURRENT DATA AUTHORITY",
    "DM100": "LOGICAL ACKNOWLEDGEMENT",
    "DM101": "REQUEST END OF SERVICE",
    "DM102": "LANDING REPORT",
    "DM103": "CANCELLING IFR",
    "DM104": "ETA [position] [time]",
    "DM105": "ALTERNATE AERODROME [airport]",
    "DM106": "PREFERRED LEVEL [level]",
    "DM107": "NOT AUTHORIZED NEXT DATA AUTHORITY",
    "DM108": "DE-ICING COMPLETE",
    "DM109": "TOP OF DESCENT [time]",
    "DM110": "TOP OF DESCENT [position]",
    "DM111": "TOP OF DESCENT [time] [position]",
    "DM112": "SQUAWKING 7500",
    "DM113": "[speed type] SPEED [speed]",
    "DM114": "CLEAR OF WEATHER",
    "DM115": "WE CAN ACCEPT [level] AT [position]",
    "DM116": "WE CAN ACCEPT [speed] AT [position]",
    "DM117": "WE CAN ACCEPT [specified distance] [direction] AT [position]"
}

# Read the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Convert Acceptable_responses to consistent format
for obj in data:
    if isinstance(obj, dict) and 'Acceptable_responses' in obj:
        acceptable_responses = obj['Acceptable_responses']
        
        if isinstance(acceptable_responses, list):
            new_responses = []
            for response in acceptable_responses:
                if isinstance(response, str):
                    # Convert string to object format
                    text = dm_mapping.get(response, f"[{response} message]")
                    new_responses.append({"ref": response, "text": text})
                elif isinstance(response, dict):
                    # Already in object format, keep as is
                    new_responses.append(response)
            
            obj['Acceptable_responses'] = new_responses

# Write the modified data back to the file
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print(f"Completed transformation of Acceptable_responses to consistent object format in {file_path}")
