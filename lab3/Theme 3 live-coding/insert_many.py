from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient("mongodb://root:root@localhost",27017)
    db = client["mydatabase"]
    collection_3 = db["collection_3"]
    result = collection_3.insert_many([
        {"name": "Amy", "address": "Apple st 652"},
        {"name": "Hannah", "address": "Mountain 21"},
        {"name": "Michael", "address": "Valley 345"}
    ])

    print(result.inserted_ids)
