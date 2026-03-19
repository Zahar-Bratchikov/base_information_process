from pymongo import MongoClient

if __name__ == "__main__":
    client = MongoClient("mongodb://root:root@localhost", 27017)
    db = client["database_logical"]
    collection = db["collection"]
    collection.insert_many(
       [{"item": "Pens", "quantity": 350, "tag": "school", "cost": 100},
        {"item": "Erasers", "quantity": 15, "tag": "office", "cost": 50},
        {"item": "Books", "quantity": 5, "tag": "home", "cost": 400},
        {"item": "Rulers", "quantity": 20, "tag": "home", "cost": 30},
        ])

    print(list(collection.find(
        {"$or": [
                {"$and": [{"quantity": {"$gt": 10}}, {"tag": "office"}]},
                {"quantity": {"$lt": 10}}]},
        {"_id": 0, "item": 1}
    )))
    collection.delete_many({})
    