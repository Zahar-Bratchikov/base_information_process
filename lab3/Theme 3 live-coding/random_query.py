from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient("mongodb://root:root@localhost", 27017)
    db = client["database_random"]
    collection = db["collection"]
    collection.insert_many(
       [
         {"name": "Archibald", "voterId": 4321, "district": 3},
         {"name": "Beckham", "voterId": 4331, "district": 3},
         {"name": "Carolin", "voterId": 5321, "district": 4},
         {"name": "Debarge", "voterId": 4343, "district": 3},
         {"name": "Eckhard", "voterId": 4161, "district": 3},
         {"name": "Faberge", "voterId": 4300, "district": 1},
         {"name": "Grimwald", "voterId": 4111, "district": 3},
         {"name": "Humphrey", "voterId": 2021, "district": 3},
         {"name": "Idelfon", "voterId": 1021, "district": 4},
         {"name": "Justo", "voterId": 9891, "district": 3}
       ]
    )

    print(list(collection.find(
        {"district": 3, "$expr": { "$lt": [0.5, {"$rand": {} } ] }},
        { "_id": 0, "name": 1}
    )))