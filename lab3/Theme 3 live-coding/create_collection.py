from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient("mongodb://root:root@localhost",27017)
    db = client["database_2"]
    collection_1 = db["collection_1"]
    collection_1.insert_one({})
    print(db.list_collection_names())
