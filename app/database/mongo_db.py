from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

URI = "mongodb+srv://datalinksDb:datalinksDbPassword@cluster0.hx4d37v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

class MongoDb:
    def __inti__(self, db_uri=URI): 
        client = MongoClient(db_uri, server_api=ServerApi('1'))
        db = client["datalinks"]
        uplinks = db["uplinks"]
        downlinks = db["downlinks"]

    
    # def find_datalink_by_ref(self, ref):

    #     return next(
    #         (msg for msg in self.uplinks.find() if msg.get("Ref_Num", "").replace(" ", "") == ref),
    #         None
    #     )