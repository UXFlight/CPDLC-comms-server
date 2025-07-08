import os
from app.database.uplinks import uplinks
from supabase import create_client, Client # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# for msg in uplinks:
#     ref_num = msg["Ref_Num"]

#     data = {
#         "ref_num": ref_num,
#         "message_intent": msg.get("Message_Intent", ""),
#         "message_element": msg.get("Message_Element", ""),
#         "response_required": msg.get("Response_required", []),
#         "acceptable_responses": msg.get("Acceptable_responses", []),
#         "category": msg.get("Category", ""),
#         "system": ["FANS 1/A"],
#         "urgency": msg.get("Urgency", "normal"),
#     }

#     response = supabase.table("datalinks").insert(data).execute()
#     print(f"{ref_num}")