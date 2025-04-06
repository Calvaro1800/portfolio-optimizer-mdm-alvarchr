import os
from dotenv import load_dotenv
from pymongo import MongoClient
from transformers import pipeline
from datetime import datetime

print("[🤖] Chargement du modèle de sentiment local...")
sentiment_model = pipeline("sentiment-analysis", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

# Chargement des variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["gainers_db"]
news_col = db["news_articles"]

# 🇫🇷 On filtre toutes les news sans sentiment (vide ou null) et avec sentiment_score 1 ou -1
target_articles = list(news_col.find({ "$or": [{"sentiment": ""}, {"sentiment": None}, {"sentiment_score": None}, {"sentiment_score": {"$in": [1, -1]}}]}))
print(f"[📄] {len(target_articles)} articles à analyser et à normaliser...")

updated_count = 0
for article in target_articles:
    try:
        if isinstance(article.get("sentiment_score"), (int, float)) and article["sentiment_score"] in [1, -1]:
            # Si le sentiment est 1 ou -1, nous le normalisons
            sentiment = "positive" if article["sentiment_score"] == 1 else "negative"
            sentiment_score = 1 if sentiment == "positive" else -1
        else:
            # Sinon, on fait une analyse classique
            result = sentiment_model(article["title"])[0]  # 🔍 Analyse du titre uniquement
            sentiment = result["label"]  # POSITIVE, NEGATIVE, NEUTRAL (prévu par le modèle)
            sentiment_score = result["score"]  # Score numérique (probabilité du modèle)

        # Mise à jour de l'article avec le sentiment et sentiment_score normalisé
        news_col.update_one(
            {"_id": article["_id"]},
            {"$set": {"sentiment": sentiment, "sentiment_score": sentiment_score, "analyzed_at": datetime.utcnow().isoformat()}}
        )
        updated_count += 1
    except Exception as e:
        print(f"[⚠️] Erreur sur l'article {article.get('_id')}: {e}")

print(f"[📌] {updated_count} articles mis à jour avec un sentiment et un score normalisé.")
client.close()
