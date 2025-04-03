# core/regression_model.py

from pymongo import MongoClient
from sklearn.linear_model import LinearRegression
import numpy as np
import os
import logging

# 🇫🇷 Connexion à MongoDB pour charger les données financières nettoyées
def load_cleaned_data():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("❌ MONGO_URI not set in environment variables")

    client = MongoClient(mongo_uri)
    db = client["gainers_db"]
    collection = db["yahoo_all_stocks"]  # ✅ On utilise désormais la collection enrichie

    documents = list(collection.find({
        "price": {"$exists": True},
        "performance": {"$exists": True}
    }))

    logging.info(f"✅ {len(documents)} documents loaded from MongoDB.")
    client.close()
    return documents

# 🇫🇷 Chargement du score de sentiment moyen stocké dans MongoDB
def load_avg_sentiment_score():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["gainers_db"]
    collection = db["avg_sentiment"]

    doc = collection.find_one()
    client.close()

    if doc and "avg_sentiment_score" in doc:
        return doc["avg_sentiment_score"]
    else:
        logging.warning("⚠️ avg_sentiment_score not found in MongoDB. Using 0.0 as fallback.")
        return 0.0

# 🇫🇷 Entraîne un modèle de régression linéaire sur les données + sentiment
def train_regression_model():
    data = load_cleaned_data()
    avg_sentiment_score = load_avg_sentiment_score()

    X = []
    y = []

    for doc in data:
        try:
            price = float(doc["price"])
            sentiment = float(avg_sentiment_score)
            X.append([price, sentiment])
            y.append(float(doc["performance"]))
        except Exception as e:
            logging.error(f"Erreur en traitant le document {doc}: {e}")

    if not X or not y:
        raise ValueError("❌ Aucune donnée suffisante pour entraîner le modèle.")

    model = LinearRegression()
    model.fit(X, y)

    logging.info("✅ Modèle de régression entraîné avec succès.")
    return model

# 🇫🇷 Fonction pour prédire la performance avec prix et sentiment
# core/regression_model.py

def predict_performance(price: float, sentiment_score: float = 0.0) -> float:
    """
    Prédit une performance future basée sur le prix actuel et le score de sentiment (optionnel).
    🇬🇧 Predicts future performance based on price and sentiment.
    🇩🇪 Sagt zukünftige Performance basierend auf Preis und Sentiment voraus.
    """
    # Exemple très simple : pondération linéaire
    predicted = price * (1 + 0.01 * sentiment_score)
    return round(predicted, 2)
