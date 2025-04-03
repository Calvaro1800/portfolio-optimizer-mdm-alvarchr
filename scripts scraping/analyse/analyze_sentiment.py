# analyze_sentiment.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from transformers import pipeline
from datetime import datetime

print("[🤖] Chargement du modèle de sentiment local...")
sentiment_model = pipeline("sentiment-analysis", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["gainers_db"]
news_col = db["news_articles"]

# 🇫🇷 On filtre toutes les news sans sentiment (vide ou null)
target_articles = list(news_col.find({ "$or": [ {"sentiment": ""}, {"sentiment": None} ] }))
print(f"[📄] {len(target_articles)} articles à analyser...")

updated_count = 0
for article in target_articles:
    try:
        result = sentiment_model(article["title"])[0]  # 🔍 Analyse du titre uniquement
        sentiment = result["label"]  # POSITIVE, NEGATIVE, NEUTRAL (prévu par le modèle)
        news_col.update_one({"_id": article["_id"]}, {"$set": {"sentiment": sentiment, "analyzed_at": datetime.utcnow().isoformat()}})
        updated_count += 1
    except Exception as e:
        print(f"[⚠️] Erreur sur l'article {article.get('_id')}: {e}")

print(f"[📌] {updated_count} articles mis à jour avec un sentiment.")
client.close()
