# 🇫🇷 Ce script ajoute un champ "performance" aléatoire pour chaque action
# 🇩🇪 Fügt jedem Dokument ein zufälliges Performance-Feld hinzu
# 🇬🇧 Adds a random performance field to each stock document

from pymongo import MongoClient
import os
import random
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)
db = client["gainers_db"]
collection = db["yahoo_all_stocks"]

updated_count = 0
for doc in collection.find():
    performance = round(random.uniform(-5, 10), 2)  # simulate performance between -5% and +10%
    result = collection.update_one({"_id": doc["_id"]}, {"$set": {"performance": performance}})
    if result.modified_count > 0:
        updated_count += 1

client.close()
print(f"[✅] {updated_count} documents mis à jour avec un champ 'performance'")
