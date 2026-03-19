from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient("mongodb://root:root@localhost", 27017)
    db = client["database_random"]
    collection = db["collection"]
    collection.insert_many(
       [{"item": 'Pens', "quantity": 350, "tag": 'school'},
        {"item": 'Erasers', "quantity": 15, "tag": 'office'},
        {"item": 'Books', "quantity": 5, "tag": 'home'}])

    print(list(collection.find(
        {"tag": {"$in": ["school", "office"]}},
        { "_id": 0, "item": 1, "tag": 1})))
    collection.delete_many({})
    