import json
from pathlib import Path
from typing import Any


DATA_DIRECTORY = Path(__file__).parent / "data"


def _load_json(filename: str) -> Any:
    path = DATA_DIRECTORY / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


class DataStore:
    """In-memory access to the application's static JSON data."""

    def __init__(self):
        uplinks = _load_json("UpLinks.json")
        downlinks = _load_json("DownLinks.json")
        supported_codes = _load_json("supported_codes.json")

        self._uplinks_by_ref = {
            record["Ref_Num"]: record for record in uplinks
        }
        self._downlinks_by_ref = {
            record["Ref_Num"]: record for record in downlinks
        }
        self._supported_codes = tuple(
            dict.fromkeys(code.strip().upper() for code in supported_codes)
        )

    @property
    def supported_codes(self) -> list[str]:
        return list(self._supported_codes)

    def is_supported_code(self, code: str) -> bool:
        return code.strip().upper() in self._supported_codes

    def find_datalink_by_ref(self, ref: str):
        records = self._uplinks_by_ref if ref.startswith("UM") else self._downlinks_by_ref
        return records.get(ref)

    def find_uplink_by_ref(self, ref: str):
        return self._uplinks_by_ref.get(ref)

    def find_downlink_by_ref(self, ref: str):
        return self._downlinks_by_ref.get(ref)


# Loaded once when the server imports the application.
data_store = DataStore()
