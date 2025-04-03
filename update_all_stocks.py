import requests
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# 🌐 Paramètres MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["gainers_db"]
collection = db["yahoo_all_stocks"]

# 📡 API Yahoo Finance (most active)
API_URL = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
PARAMS = {
    "formatted": "true",
    "scrIds": "most_actives",
    "start": "0",
    "count": "100"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def extract_float(value):
    if isinstance(value, dict):
        return float(value.get("raw", 0))
    try:
        return float(value)
    except:
        return 0.0

def extract_int(value):
    if isinstance(value, dict):
        return int(value.get("raw", 0))
    try:
        return int(value)
    except:
        return 0

def transform_quote(quote):
    try:
        return {
            "_id": quote["symbol"],
            "name": quote.get("shortName", "N/A"),
            "price": extract_float(quote.get("regularMarketPrice")),
            "change": extract_float(quote.get("regularMarketChange")),
            "percent_change": extract_float(quote.get("regularMarketChangePercent")),
            "volume": extract_int(quote.get("regularMarketVolume")),
            "scraped_at": datetime.utcnow()
        }
    except Exception as e:
        print(f"[⚠️] Erreur transformation quote {quote.get('symbol', '')} : {e}")
        return None

def main():
    print("\n[🔍] Requête API Yahoo Finance...")

    try:
        response = requests.get(API_URL, headers=HEADERS, params=PARAMS)
        data = response.json()

        quotes = data["finance"]["result"][0]["quotes"]
        print(f"[✅] {len(quotes)} actions reçues via l'API.")

        transformed = [transform_quote(q) for q in quotes]
        cleaned = [q for q in transformed if q is not None]

        if not cleaned:
            print("[⚠️] Aucune action valide à enregistrer.")
            return

        collection.delete_many({})
        collection.insert_many(cleaned)
        print(f"[📦] {len(cleaned)} actions enregistrées dans la collection 'yahoo_all_stocks'.")
    except Exception as e:
        print(f"[❌] Erreur globale : {e}")

if __name__ == "__main__":
    main()
