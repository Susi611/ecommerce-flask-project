from pymongo import MongoClient

uri = "mongodb+srv://susisushanthini_db_user:Susi12345@cluster0.ttnchb1.mongodb.net/EcommerceDB?retryWrites=true&w=majority"

try:
    client = MongoClient(uri)
    print(client.list_database_names())
    print("Connected Successfully")
except Exception as e:
    print("Connection Failed")
    print(e)