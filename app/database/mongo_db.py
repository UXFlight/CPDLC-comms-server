import os
from pymongo.mongo_client import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi

URI = os.getenv('MONGODB_URI')
MONGO_TIMEOUT_MS = int(os.getenv("MONGODB_TIMEOUT_MS", "1500"))

class MongoDb:
    def __init__(self, db_uri=URI):
        self.client = MongoClient(
            db_uri,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=MONGO_TIMEOUT_MS,
            connectTimeoutMS=MONGO_TIMEOUT_MS,
            socketTimeoutMS=MONGO_TIMEOUT_MS,
        )
        db_datalinks = self.client["datalinks"]
        db_users = self.client["users"]
        self.uplinks = db_datalinks["uplinks"]
        self.downlinks = db_datalinks["downlinks"]
        self.atcs = db_users["atc"]

    def _safe_find_one(self, collection, query):
        try:
            return collection.find_one(query)
        except PyMongoError as e:
            print(f"[MongoDb] Query failed on '{collection.name}': {e}")
            return None

    def find_datalink_by_ref(self, ref):
        #type = "downlinks" if "DM" in ref else "uplinks" autre facon de faire
        #return self.db[type].find_one({"Ref_Num": ref})
        type = self.uplinks if "UM" in ref else self.downlinks
        return self._safe_find_one(type, {"Ref_Num": ref})
    
    def find_UM_by_ref(self, ref):
        return self._safe_find_one(self.uplinks, {"Ref_Num": ref})
    
    def find_DM_by_ref(self, ref):
        return self._safe_find_one(self.downlinks, {"Ref_Num": ref})
    
    def find_available_atc(self, atc_unit):
        if not atc_unit:
            return None
        atc = self._safe_find_one(self.atcs, {"atc_unit": atc_unit})
        if not atc:
            return None
        return atc if atc.get("available") else None


## Global MangoDb instance
mongo_db = MongoDb()
