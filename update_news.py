# update_news.py

import os
import time
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient, UpdateOne
import requests
from bs4 import BeautifulSoup

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client["gainers_db"]
gainers_col = db["yahoo_gainers"]
news_col = db["news_by_symbol"]

# Récupération des symboles (🇫🇷 sauvegardés sous "_id")
symbols = [doc["_id"] for doc in gainers_col.find({}, {"_id": 1})]

# 🇬🇧 Scrape latest news per symbol from Yahoo Finance
def scrape_news_for_symbol(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}?p={symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        news_items = soup.select("li.js-stream-content")
        articles = []
        for item in news_items:
            title_tag = item.select_one("h3 a")
            if not title_tag:
                continue
            title = title_tag.text.strip()
            link = "https://finance.yahoo.com" + title_tag["href"]
            articles.append({
                "symbol": symbol,
                "title": title,
                "link": link,
                "scraped_at": datetime.utcnow().isoformat(),
                "sentiment": ""
            })
            if len(articles) >= 1:
                break
        return articles
    except Exception as e:
        print(f"[⚠️] Erreur scraping {symbol}: {e}")
        return []

# Scraping des actualités symbol par symbol
all_articles = []
for sym in symbols:
    news = scrape_news_for_symbol(sym)
    if news:
        all_articles.extend(news)
    time.sleep(1.5)

# Si moins de 5 news récupérées, on complète avec des news générales
if len(all_articles) < 5:
    print("[ℹ️] Moins de 5 news spécifiques trouvées — chargement de news générales…")
    try:
        resp = requests.get("https://finance.yahoo.com/topic/latest-news", headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        news_items = soup.select("li.js-stream-content h3 a")
        for item in news_items:
            title = item.text.strip()
            link = "https://finance.yahoo.com" + item["href"]
            all_articles.append({
                "symbol": "general",
                "title": title,
                "link": link,
                "scraped_at": datetime.utcnow().isoformat(),
                "sentiment": ""
            })
            if len(all_articles) >= 5:
                break
    except Exception as e:
        print(f"[⚠️] Erreur scraping news générales: {e}")

# Insertion dans MongoDB sans doublons (par symbol + titre)
ops = []
for article in all_articles:
    ops.append(UpdateOne(
        {"symbol": article["symbol"], "title": article["title"]},
        {"$setOnInsert": article},
        upsert=True
    ))

if ops:
    result = news_col.bulk_write(ops)
    print(f"[✅] {result.upserted_count} nouveaux articles insérés.")
else:
    print("[ℹ️] Aucun nouvel article trouvé.")

client.close()
