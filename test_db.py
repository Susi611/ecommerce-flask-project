from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://susisushanthini_db_user:Susi@12345@cluster0.ttnchb1.mongodb.net/EcommerceDB?retryWrites=true&w=majority"
)

db = client["EcommerceDB"]

print(db.list_collection_names())