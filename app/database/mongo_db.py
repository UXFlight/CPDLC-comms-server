from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

URI = "mongodb+srv://datalinksDb:datalinksDbPassword@cluster0.hx4d37v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

class MongoDb:
    def __init__(self, db_uri=URI): 
        client = MongoClient(db_uri, server_api=ServerApi('1'))
        db = client["datalinks"]
        self.uplinks = db["uplinks"]
        self.downlinks = db["downlinks"]

    def find_datalink_by_ref(self, ref):
        #type = "downlinks" if "DM" in ref else "uplinks" autre facon de faire
        #return self.db[type].find_one({"Ref_Num": ref})
        type = self.uplinks if "UM" in ref else self.downlinks
        return type.find_one({"Ref_Num": ref})
    
    