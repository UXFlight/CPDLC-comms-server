from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from app.database.data.uplinks import uplinks
from app.database.data.downlinks import downlinks
from app.database.data.atc import atcs

uri = "mongodb+srv://datalinksDb:datalinksDbPassword@cluster0.hx4d37v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

    # db = client["datalinks"]
    # uplinks_coll = db["uplinks"]
    # downlinks_coll = db["downlinks"]

    db = client["users"]
    atc_coll = db["atc"]
    atc_coll.drop()
    atc_coll.insert_many(atcs)
    # populate the collections with data
    # uplinks_coll.insert_many(uplinks)
    # downlinks_coll.insert_many(downlinks)


except Exception as e:
    print(e)