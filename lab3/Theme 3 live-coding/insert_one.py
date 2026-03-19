from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient("mongodb://root:root@localhost",27017)
    db = client["database_2"]
    collection_2 = db["collection_2"]
    result = collection_2.insert_one({ "name": "John", "address": "Highway 37" })
    print(result.inserted_id)
