#!/usr/bin/env python3
import json

# Path to the DownLinks.json file
file_path = r"c:\Users\irina\OneDrive\Desktop\CPDLC-comms-server\app\database\DownLinks.json"

# Read the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Convert Acceptable_responses from array of arrays to simple array of strings
for obj in data:
    if isinstance(obj, dict) and 'Acceptable_responses' in obj:
        acceptable_responses = obj['Acceptable_responses']
        
        if isinstance(acceptable_responses, list):
            # Flatten the array of arrays into a simple array
            flattened = []
            for response in acceptable_responses:
                if isinstance(response, list):
                    # If it's an array, add all its elements
                    flattened.extend(response)
                else:
                    # If it's a single string, add it directly
                    flattened.append(response)
            
            # Update the field with the flattened array
            obj['Acceptable_responses'] = flattened

# Write the modified data back to the file
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print(f"Converted Acceptable_responses to simple arrays of strings in {file_path}")
