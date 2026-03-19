from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient("mongodb://root:root@localhost",27017)
    db = client["database_1"]
    db.test.insert_one({})
    print(client.list_database_names())
