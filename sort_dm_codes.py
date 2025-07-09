#!/usr/bin/env python3
import json
import re

# Path to the DownLinks.json file
file_path = r"c:\Users\irina\OneDrive\Desktop\CPDLC-comms-server\app\database\UpLinks.json"

# Read the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Function to extract DM number for sorting
def get_dm_number(obj):
    ref_num = obj.get('Ref_Num', '')
    if ref_num.startswith('UM '):
        # Extract the number after "DM "
        match = re.search(r'UM (\d+)', ref_num)
        if match:
            return int(match.group(1))
    return float('inf')  # Put items without valid DM numbers at the end

# Sort the data by DM number
sorted_data = sorted(data, key=get_dm_number)

# Write the sorted data back to the file
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(sorted_data, file, indent=2, ensure_ascii=False)

print(f"Sorted UM codes in ascending order in {file_path}")

# Print the order of DM codes for verification
print("\nUM codes order:")
for obj in sorted_data:
    ref_num = obj.get('Ref_Num', 'No Ref_Num')
    if ref_num != 'No Ref_Num' and ref_num.startswith('UM '):
        print(ref_num)
