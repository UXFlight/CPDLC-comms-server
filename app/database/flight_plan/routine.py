import json
from pathlib import Path

# Chargement unique du JSON
json_path = Path(__file__).parent / "routine.json"
with open(json_path, "r", encoding="utf-8") as f:
    routine = json.load(f)
