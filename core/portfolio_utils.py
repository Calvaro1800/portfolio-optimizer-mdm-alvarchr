# core/portfolio_utils.py

import pandas as pd
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")


def load_cleaned_data():
    """
    🇫🇷 Charge les données nettoyées depuis MongoDB.
    🇩🇪 Lädt die bereinigten Daten aus MongoDB.
    🇬🇧 Loads cleaned data from MongoDB.
    """
    print("[INFO] Chargement des données MongoDB nettoyées…")
    client = MongoClient(MONGO_URI)
    db = client["gainers_db"]
    collection = db["yahoo_gainers"]

    try:
        pipeline = [
            {"$match": {"change": {"$ne": None}}},
            {"$project": {
                "_id": 1,
                "price": "$price",
                "volume": "$volume",
                "market_cap": "$market_cap",
                "performance": "$change"
            }}
        ]

        data = list(collection.aggregate(pipeline))
        df = pd.DataFrame(data)

        print(f"[✅] {len(df)} documents chargés depuis MongoDB.")
        if not df.empty:
            print("[✅] Exemple de données chargées :")
            print(df.head(10))

        return df

    finally:
        client.close()  # ✅ Ferme proprement


def compute_sharpe_ratio(portfolio: dict, stock_data: dict, volatility: float = 0.2, risk_free_rate: float = 0.01) -> float:
    """
    🇫🇷 Calcule le Sharpe Ratio moyen à partir des performances des actions du portefeuille.
    🇩🇪 Berechnet das durchschnittliche Sharpe-Verhältnis basierend auf der Aktienperformance im Portfolio.
    🇬🇧 Computes average Sharpe Ratio from stock performances in the portfolio.

    :param portfolio: dict comme {'AAPL': 10, 'TSLA': 5}
    :param stock_data: dict comme {'AAPL': {'performance': 0.05}, ...}
    :param volatility: volatilité fixée (ex: 0.2)
    :param risk_free_rate: taux sans risque (ex: 0.01)
    :return: Sharpe Ratio du portefeuille
    """
    returns = []

    for symbol, quantity in portfolio.items():
        data = stock_data.get(symbol)
        if data and 'performance' in data:
            returns.append(data['performance'])

    if not returns:
        return 0.0

    avg_return = sum(returns) / len(returns)
    sharpe_ratio = (avg_return - risk_free_rate) / volatility
    return round(sharpe_ratio, 2)
