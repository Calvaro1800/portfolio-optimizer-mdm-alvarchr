import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone

# 🇫🇷 Chargement des variables d’environnement (.env)
load_dotenv()

# 🇩🇪 Verbindung zur MongoDB-Datenbank
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["gainers_db"]
collection = db["yahoo_gainers"]

# 🇬🇧 Yahoo Finance API endpoint for top gainers
YF_API = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrIds=day_gainers&count=25"

def fetch_yahoo_gainers():
    print("[INFO] Scraping Yahoo Finance via API…")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(YF_API, headers=headers)
        data = response.json()
    except Exception as e:
        print(f"[❌] Request failed: {e}")
        return

    if "finance" not in data or "result" not in data["finance"]:
        print("[❌] Format inattendu.")
        return

    results = data["finance"]["result"][0].get("quotes", [])
    print(f"[INFO] {len(results)} gagnants trouvés.")

    if not results:
        print("[⚠️] Aucun gagnant trouvé, la collection MongoDB n’a PAS été modifiée.")
        return

    # 💥 Suppression des anciens documents
    collection.delete_many({})
    print("[INFO] Ancienne collection vidée.")

    for item in results:
        try:
            doc = {
                "_id": item["symbol"],
                "name": item.get("shortName", item.get("longName", "")),
                "price": item.get("regularMarketPrice"),
                "change": item.get("regularMarketChange"),
                "percent_change": item.get("regularMarketChangePercent"),
                "volume": item.get("regularMarketVolume"),
                "market_cap": item.get("marketCap"),
                "timestamp": datetime.now(timezone.utc)
            }

            if doc["price"] is None:
                raise ValueError("Pas de prix valide")

            collection.insert_one(doc)
            print(f"[✓] {doc['_id']} à {doc['price']} USD")

        except Exception as e:
            print(f"[!] Erreur {item.get('symbol')}: {e}")

    print(f"[🧾] Total documents MongoDB : {collection.count_documents({})}")
    print("[✅] Import via API terminé.")

if __name__ == "__main__":
    fetch_yahoo_gainers()
