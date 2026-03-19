from pymongo import MongoClient

if __name__ == "__main__":
    client = MongoClient("mongodb://root:root@localhost", 27017)
    db = client["database_count"]
    collection = db["collection"]
    collection.insert_many(
       [{"item": "Pens", "quantity": 350, "tag": "school", "cost": 100},
        {"item": "Erasers", "quantity": 15, "tag": "office", "cost": 50},
        {"item": "Books", "quantity": 5, "tag": "home", "cost": 400},
        {"item": "Rulers", "quantity": 20, "tag": "home", "cost": 30},
        ])
    print(collection.count_documents({"tag": "home"}))
    collection.delete_many({})
    