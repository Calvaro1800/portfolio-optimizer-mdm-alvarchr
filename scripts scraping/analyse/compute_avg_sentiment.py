# compute_avg_sentiment.py

import os
from dotenv import load_dotenv
from datetime import datetime, UTC
from pymongo import MongoClient

# 🇫🇷 Charger les variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# 🇬🇧 Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["gainers_db"]
news_col = db["news_articles"]
stats_col = db["sentiment_stats"]

print("📚 Chargement des articles avec un sentiment_score...")

# 🇫🇷 Filtrer les articles qui ont un score de sentiment numérique
articles = list(news_col.find({"sentiment_score": {"$exists": True}}))

if not articles:
    print("⚠️ Aucun article avec score de sentiment trouvé.")
    exit()

# 🇩🇪 Durchschnitt berechnen (calculate mean)
scores = [art["sentiment_score"] for art in articles if isinstance(art["sentiment_score"], (int, float))]
avg_score = round(sum(scores) / len(scores), 4)

# 🇬🇧 Store in a new collection
stats_col.insert_one({
    "avg_sentiment_score": avg_score,
    "article_count": len(scores),
    "computed_at": datetime.now(UTC).isoformat()
})

print(f"[✅] Moyenne du sentiment : {avg_score} (sur {len(scores)} articles)")
print("[📝] Stockée dans la collection 'sentiment_stats'.")

client.close()

