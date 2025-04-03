from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["your_database_name"]
collection = db["yahoo_gainers"]

def load_cleaned_data():
    pipeline = [  # le pipeline de formatage qu’on a créé dans Compass
        {
            "$addFields": {
                "_id": "$symbol",
                "performance": "$change"
            }
        },
        {
            "$project": {
                "symbol": 0,
                "change": 0,
                "percent_change": 0
            }
        }
    ]
    return list(collection.aggregate(pipeline))
