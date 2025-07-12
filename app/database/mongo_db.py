from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

URI = "mongodb+srv://datalinksDb:datalinksDbPassword@cluster0.hx4d37v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

class MongoDb:
    def __init__(self, db_uri=URI): 
        client = MongoClient(db_uri, server_api=ServerApi('1'))
        db_datalinks = client["datalinks"]
        db_users = client["users"]
        self.uplinks = db_datalinks["uplinks"]
        self.downlinks = db_datalinks["downlinks"]
        self.atcs = db_users["atc"]

    def find_datalink_by_ref(self, ref):
        #type = "downlinks" if "DM" in ref else "uplinks" autre facon de faire
        #return self.db[type].find_one({"Ref_Num": ref})
        print(f"Searching for datalink with ref: {ref}")
        type = self.uplinks if "UM" in ref else self.downlinks
        return type.find_one({"Ref_Num": ref})
    
    def find_available_atc(self, atc_unit):
        atc = self.atcs.find_one({"atc_unit": atc_unit})
        return atc if atc.get("available") else None
