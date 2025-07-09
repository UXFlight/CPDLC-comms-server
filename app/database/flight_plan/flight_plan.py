import json
from pathlib import Path

# Chargement unique du JSON
json_path = Path(__file__).parent / "flight_plan_cyul_kfll.json"
with open(json_path, "r", encoding="utf-8") as f:
    flight_plan = json.load(f)
