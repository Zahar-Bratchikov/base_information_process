from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient("mongodb://root:root@localhost",27017)
    db = client["database"]
    collection = db["collection_8"]
    collection.insert_many([
        {"name": "Amy", "address": "Apple st 652"},
        {"name": "Hannah", "address": "Mountain 21"},
        {"name": "Michael", "address": "Valley 345"}
    ])
    
    print(list(collection.find({},{ "_id": 0, "name": 1})))
