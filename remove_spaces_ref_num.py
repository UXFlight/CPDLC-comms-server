#!/usr/bin/env python3
import json
import re

# Path to the DownLinks.json file
file_path = r"c:\Users\irina\OneDrive\Desktop\CPDLC-comms-server\app\database\UpLinks.json"

# Read the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Remove spaces in Ref_Num between DM and number
for obj in data:
    if isinstance(obj, dict) and 'Ref_Num' in obj:
        # Remove space between DM and number (e.g., "DM 0" becomes "DM0")
        obj['Ref_Num'] = re.sub(r'UM\s+(\d+)', r'UM\1', obj['Ref_Num'])

# Write the modified data back to the file
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print(f"Removed spaces in Ref_Num between UM and numbers in {file_path}")
