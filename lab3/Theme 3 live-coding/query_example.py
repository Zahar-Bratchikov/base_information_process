from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient("mongodb://root:root@localhost", 27017)
    db = client["database"]
    collection = db["collection_10"]
    collection.insert_many([
        {"model": "BMW", "cost": 100},
        {"model": "Mercedes", "cost": 80},
        {"model": "Ferrari", "cost": 200}
    ])

    print(list(collection.find({
        "cost":{"$gt": 90, "$lt": 110}
    })))
