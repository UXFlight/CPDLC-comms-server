#!/usr/bin/env python3
import json

# Path to the DownLinks.json file
file_path = r"c:\Users\irina\OneDrive\Desktop\CPDLC-comms-server\app\database\data\DownLinks.json"

# Mapping of UM codes to their text descriptions
um_mapping = {
    "UM0": "WILCO",
    "UM1": "UNABLE",
    "UM2": "STANDBY",
    "UM3": "ROGER",
    "UM4": "AFFIRM",
    "UM5": "NEGATIVE",
    "UM19": "MAINTAIN [level]",
    "UM20": "CLIMB TO [level]",
    "UM23": "DESCEND TO [level]",
    "UM26": "CLIMB TO REACH [level] BY [time]",
    "UM27": "DESCEND TO REACH [level] BY [time]",
    "UM28": "CLIMB TO REACH [level] BY [position]",
    "UM29": "DESCEND TO REACH [level] BY [position]",
    "UM46": "CLIMB AT [vertical rate] MINIMUM",
    "UM47": "CLIMB AT [vertical rate] MAXIMUM", 
    "UM48": "DESCEND AT [vertical rate] MINIMUM",
    "UM55": "FLY PRESENT HEADING",
    "UM61": "FLY HEADING [degrees]",
    "UM64": "OFFSET [specified distance] [direction] OF ROUTE",
    "UM74": "PROCEED DIRECT TO [position]",
    "UM82": "AT [position] FLY HEADING [degrees]",
    "UM96": "AT [time] FLY HEADING [degrees]",
    "UM103": "EXPECT CLIMB AT [time]",
    "UM104": "EXPECT CLIMB AT [position]",
    "UM105": "EXPECT DESCENT AT [time]",
    "UM106": "FLY AT [speed]",
    "UM107": "INCREASE SPEED TO [speed]",
    "UM108": "REDUCE SPEED TO [speed]",
    "UM109": "RESUME NORMAL SPEED",
    "UM116": "REDUCE SPEED TO [speed] OR GREATER",
    "UM159": "ALTIMETER [setting]",
    "UM162": "ERROR [error information]",
    "UM183": "ATIS [atis code]",
    "UM190": "AT [position] FLY HEADING [degrees]",
    "UM211": "FREE TEXT [free text]",
    "UM222": "INCREASE SPEED TO [speed] OR GREATER"
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
                    text = um_mapping.get(response, f"[{response} message]")
                    new_responses.append({"ref": response, "text": text})
                elif isinstance(response, dict):
                    # Already in object format, keep as is
                    new_responses.append(response)
            
            obj['Acceptable_responses'] = new_responses

# Write the modified data back to the file
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print(f"Completed transformation of Acceptable_responses to consistent object format in {file_path}")
