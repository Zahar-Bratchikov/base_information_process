from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient("mongodb://root:root@localhost",27017)
    db = client["database"]
    collection = db["collection_4"]
    result = collection.insert_many([
        {"_id": 2, "name": "Amy", "address": "Apple st 652"},
        {"_id": 3, "name": "Hannah", "address": "Mountain 21"},
        {"_id": 4, "name": "Michael", "address": "Valley 345"}
    ])
    
    print(result.inserted_ids)
