# update_sentiment_score.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient

# 📦 Charger les variables d’environnement
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# 🔌 Connexion à MongoDB
client = MongoClient(MONGO_URI)
db = client["gainers_db"]
collection = db["news_articles"]

# 🎯 Mapping texte → score
sentiment_to_score = {"positive": 1, "neutral": 0, "negative": -1}

print("🔄 Mise à jour des champs sentiment_score...")

docs = list(collection.find({"sentiment": {"$exists": True}}))
updated_count = 0

for doc in docs:
    sentiment = doc.get("sentiment")
    if sentiment in sentiment_to_score:
        score = sentiment_to_score[sentiment]
        result = collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"sentiment_score": score}}
        )
        if result.modified_count > 0:
            updated_count += 1

print(f"[✅] {updated_count} documents mis à jour avec un score.")
client.close()

