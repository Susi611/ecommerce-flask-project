from pymongo import MongoClient

client = MongoClient("YOUR_MONGODB_ATLAS_URL")

db = client["EcommerceDB"]

products = db["products"]

products.insert_many([
    {
        "name":"Nike Air Max",
        "price":"2999",
        "image":"https://images.unsplash.com/photo-1542291026-7eec264c27ff"
    },
    {
        "name":"Adidas Ultraboost",
        "price":"3499",
        "image":"https://images.unsplash.com/photo-1460353581641-37baddab0fa2"
    },
    {
        "name":"Puma RS-X",
        "price":"2599",
        "image":"https://images.unsplash.com/photo-1514989940723-e8e51635b782"
    },
    {
        "name":"Reebok Classic",
        "price":"1999",
        "image":"https://images.unsplash.com/photo-1600185365483-26d7a4cc7519"
    },
    {
        "name":"New Balance 574",
        "price":"3299",
        "image":"https://images.unsplash.com/photo-1543508282-6319a3e2621f"
    }
])

print("Products Added")