from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient("mongodb://root:root@localhost:27017/")
    client.test.test.insert_one({})
