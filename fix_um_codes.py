#!/usr/bin/env python3
import json
import re

# Path to the DownLinks.json file
file_path = r"c:\Users\irina\OneDrive\Desktop\CPDLC-comms-server\app\database\DownLinks.json"

def fix_um_codes(data):
    """Fix UM codes to be properly formatted (e.g., UM48, UM163)"""
    if isinstance(data, list):
        result = []
        i = 0
        while i < len(data):
            if isinstance(data[i], str) and data[i].strip().upper() == "UM":
                # If we find "UM" followed by a number, combine them
                if i + 1 < len(data) and isinstance(data[i + 1], str) and data[i + 1].strip().isdigit():
                    combined = f"UM{data[i + 1].strip()}"
                    result.append(combined)
                    i += 2  # Skip the next element as we've combined it
                else:
                    result.append(data[i])
                    i += 1
            elif isinstance(data[i], str) and data[i].strip().isdigit():
                # Check if the previous element was "UM" and we missed it
                if len(result) > 0 and result[-1].strip().upper() == "UM":
                    # Replace the last "UM" with "UM" + number
                    result[-1] = f"UM{data[i].strip()}"
                    i += 1
                else:
                    # Handle cases where UM and number might be in one string but separated
                    if isinstance(data[i], str):
                        fixed = re.sub(r'UM\s+(\d+)', r'UM\1', data[i])
                        result.append(fixed)
                    else:
                        result.append(data[i])
                    i += 1
            else:
                if isinstance(data[i], str):
                    # Also handle cases where UM and number might be in one string but separated
                    fixed = re.sub(r'UM\s+(\d+)', r'UM\1', data[i])
                    result.append(fixed)
                else:
                    result.append(data[i])
                i += 1
        return result
    return data

# Read the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Fix UM codes in Response_required and Acceptable_responses fields
for obj in data:
    if isinstance(obj, dict):
        # Fix Response_required field
        if 'Response_required' in obj:
            obj['Response_required'] = fix_um_codes(obj['Response_required'])
        
        # Fix Acceptable_responses field
        if 'Acceptable_responses' in obj:
            if isinstance(obj['Acceptable_responses'], list):
                fixed_responses = []
                for response_group in obj['Acceptable_responses']:
                    if isinstance(response_group, list):
                        fixed_group = fix_um_codes(response_group)
                        fixed_responses.append(fixed_group)
                    else:
                        fixed_responses.append(response_group)
                obj['Acceptable_responses'] = fixed_responses

# Write the modified data back to the file
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print(f"Fixed UM codes in {file_path}")
