#!/usr/bin/env python3
import json
import re

# Path to the UpLinks.json file
file_path = r"c:\Users\irina\OneDrive\Desktop\CPDLC-comms-server\app\database\UpLinks.json"

def convert_response_required(value):
    """Convert Response_required to array of strings, handling 'or' cases"""
    if isinstance(value, list):
        # Already an array, ensure all elements are strings
        return [str(item) for item in value]
    elif isinstance(value, str):
        # Split by "or" and clean up each part
        parts = value.split(" or ")
        result = []
        for part in parts:
            cleaned = part.strip()
            if cleaned:  # Only add non-empty strings
                result.append(cleaned)
        return result
    else:
        return [str(value)]

# Read the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Convert Response_required fields
for obj in data:
    if isinstance(obj, dict):
        if 'Response_required' in obj:
            obj['Response_required'] = convert_response_required(obj['Response_required'])
        # Also handle Response_required_required (typo in the data)
        if 'Response_required_required' in obj:
            obj['Response_required'] = convert_response_required(obj['Response_required_required'])
            del obj['Response_required_required']  # Remove the typo field

# Write the modified data back to the file
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print(f"Converted Response_required to arrays of strings in {file_path}")
