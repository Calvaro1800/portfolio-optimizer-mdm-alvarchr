#!/bin/bash

echo ""
echo "📦 Welcome to the Portfolio Optimizer launcher"
echo "---------------------------------------------"
echo "1️⃣  Run Flask app locally"
echo "2️⃣  Build & run Docker container"
echo "3️⃣  Run scrapers (gainers + news + all stocks + sentiment)"
echo "4️⃣  Full automation (scrape + build + run)"
echo "5️⃣  Run with Gunicorn (port 5050)"
echo "❌  Quit"
echo "---------------------------------------------"
read -p "➡️  Choose an option [1-5]: " option

case $option in
  
    1)

    echo "🚀 Launching Flask app locally on port 5151..."
    export FLASK_APP=app.py
    flask run --host=0.0.0.0 --port=5151
    ;;

  2)
    echo "🐳 Building Docker container..."
    docker build -t portfolio-optimizer .
    echo "🚀 Running container..."
    docker run -p 5000:5000 -v $(pwd)/models:/app/models --env-file .env portfolio-optimizer
    ;;
  3)
    echo "🔁 Starting all scrapers..."

    echo "[1/4] 🔍 Scraping top gainers via API..."
    python update_gainers.py || echo "❌ Failed to scrape gainers"

    echo "[2/4] 📈 Scraping all stocks..."
    python update_all_stocks.py || echo "❌ Failed to scrape all stocks"

    echo "[3/4] 📰 Scraping financial news..."
    python update_news.py || echo "❌ Failed to scrape news"

    echo "[4/4] 🧠 Running sentiment analysis..."
    curl http://127.0.0.1:5000/analyze-news-local || echo "❌ Sentiment analysis failed (check if Flask is running)"

    echo "✅ All scrapers and analysis completed!"
    ;;
  4)
    echo "🔁 Starting full automation pipeline..."

    echo "🔍 Scraping top gainers..."
    python update_gainers.py || echo "❌ Failed to scrape gainers"

    echo "📈 Scraping all stocks..."
    python update_all_stocks.py || echo "❌ Failed to scrape all stocks"

    echo "📰 Scraping financial news..."
    python update_news.py || echo "❌ Failed to scrape news"

    echo "🧠 Running local sentiment analysis..."
    curl http://127.0.0.1:5000/analyze-news-local || echo "❌ Sentiment analysis failed (check if Flask is running)"

    echo "🐳 Building and running Docker container..."
    docker build -t portfolio-optimizer .
    docker run -p 5000:5000 -v $(pwd)/models:/app/models --env-file .env portfolio-optimizer
    ;;
  5)
    echo "🧼 Cleaning port 5050 (if occupied)..."
    kill -9 $(lsof -t -i :5050) 2>/dev/null

    echo "🚀 Launching Gunicorn on port 5050..."
    export PORT=5050
    gunicorn app:app --bind=0.0.0.0:$PORT --timeout 600
    ;;
  *)
    echo "👋 Exiting. Bye!"
    exit 0
    ;;
esac
