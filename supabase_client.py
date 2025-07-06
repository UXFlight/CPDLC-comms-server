import os
from app.database.downlinks import downlinks
from supabase import create_client, Client # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

import re

def parse_responses(response_str: str):
    response_str = response_str.strip()
    if not response_str:
        return []

    result = []

    if response_str.startswith("Y") or response_str.startswith("N"):
        result.append(response_str[0])
        response_str = response_str[1:].strip()

    tokens = re.findall(r"UM\s\d+(?:\s\+\sUM\s\d+)?", response_str)

    for token in tokens:
        if "+" in token:
            parts = [part.strip() for part in token.split("+")]
            result.append(parts)
        else:
            result.append(token.strip())

    return result


for msg in downlinks:
    ref_num = msg["Ref_Num"]
    message_type = "DM" if "DM" in ref_num else "UM"

    data = {
        "ref_num": ref_num,
        "type": message_type,
        "message_intent": msg.get("Message_Intent", ""),
        "message_element": msg.get("Message_Element", ""),
        "response": parse_responses(msg.get("Response", "")),
        "category": msg.get("Category", ""),
        "system": "FANS 1/A",
        "urgency": "Normal",
        "free_text": "free text" in msg.get("Message_Intent", "").lower()
    }

    response = supabase.table("datalinks").insert(data).execute()
    print(f"{ref_num}")