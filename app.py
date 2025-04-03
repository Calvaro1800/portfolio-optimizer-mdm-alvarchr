import os
import base64
from io import BytesIO
import pandas as pd
import matplotlib # type: ignore
matplotlib.use('Agg')
import matplotlib.pyplot as plt # type: ignore
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from dotenv import load_dotenv
from transformers import pipeline

# 📦 Core IA
from core.regression_model import predict_performance
from core.classifier import classify_sharpe
from core.llm_advisor import generate_financial_advice
from core.portfolio_utils import load_cleaned_data

# 🔐 Variables d’environnement
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'

client = MongoClient(os.getenv("MONGO_URI"))
db = client["gainers_db"]

@app.route('/')
def index():
    return render_template('index.html')

# ✅ Corrigé : route LLM sans context
@app.route('/ask-llm', methods=['POST'])
def ask_llm():
    try:
        data = request.get_json()
        question = data.get("question", "")
        sentiment_score = float(data.get("sentiment_score", 0.0))
        price = float(data.get("price", 100))
        gainers_list = data.get("gainers_list", [])
        portfolio = data.get("portfolio", {})
        sharpe_value = float(data.get("sharpe_value", 0.0))
        transactions = data.get("transactions", "")

        if not question:
            return jsonify({"status": "error", "message": "No question provided"}), 400

        answer = generate_financial_advice(
            question=question,
            sentiment_score=sentiment_score,
            gainers_list=gainers_list,
            portfolio=portfolio,
            sharpe_value=sharpe_value,
            transactions=transactions
        )

        performance = predict_performance(price, sentiment_score)
        sharpe = (performance - 0.02) / 0.2
        classification = classify_sharpe(sharpe)

        return jsonify({
            "status": "success",
            "answer": answer,
            "prediction": performance,
            "sharpe": sharpe,
            "classification": classification
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"LLM error: {str(e)}"}), 500

# 📤 Upload de portefeuille
@app.route('/upload', methods=['POST'])
def upload_portfolio():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"status": "error", "message": "No file uploaded"}), 400

        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(file)
        elif ext in [".xls", ".xlsx"]:
            df = pd.read_excel(file)
        else:
            return jsonify({"status": "error", "message": "Invalid file type"}), 400

        df = df[['Symbol', 'Quantity']]
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        summary = df.groupby('Symbol')['Quantity'].sum().to_dict()

        fig, ax = plt.subplots()
        ax.pie(summary.values(), labels=summary.keys(), autopct='%1.1f%%')
        plt.title("Portfolio Allocation")
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return jsonify({
            "status": "success",
            "summary": summary,
            "chart": chart_base64
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 📊 Calcul des métriques du portefeuille
@app.route('/portfolio-metrics', methods=['POST'])
def portfolio_metrics():
    try:
        data = request.get_json()
        portfolio = data.get("portfolio", {})

        if not portfolio:
            return jsonify({"status": "error", "message": "Empty portfolio"}), 400

        df = load_cleaned_data()
        df = df[df['_id'].isin(portfolio.keys())]
        df['quantity'] = df['_id'].map(portfolio)
        df['weighted_perf'] = df['performance'] * df['quantity']

        avg_perf = df['weighted_perf'].sum() / df['quantity'].sum()
        volatility = 0.2
        sharpe = (avg_perf - 0.02) / volatility

        return jsonify({
            "status": "success",
            "average_performance": round(avg_perf, 4),
            "sharpe_ratio": round(sharpe, 4),
            "volatility_used": volatility
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🔎 Recherche d’un symbole précis
@app.route('/search-symbol', methods=['POST'])
def search_symbol():
    user_input = request.json.get('query', '').strip().lower()
    if not user_input:
        return jsonify({"status": "error", "message": "Empty search input"})

    coll = db['yahoo_all_stocks']
    result = coll.find_one({
        "$or": [
            {"_id": user_input.upper()},
            {"name": {"$regex": user_input, "$options": "i"}},
        ]
    })

    if result:
        result['_id'] = str(result['_id'])
        return jsonify({"status": "found", "data": [result]})
    return jsonify({"status": "not_found", "message": f"No stock found for '{user_input}'"})

# 🧠 Autocomplétion
@app.route('/autocomplete-symbols', methods=['POST'])
def autocomplete_symbols():
    query = request.json.get('query', '').strip().lower()
    if not query:
        return jsonify({"status": "error", "matches": []})

    coll = db['yahoo_all_stocks']
    results = coll.find({
        "$or": [
            {"_id": {"$regex": f"^{query}", "$options": "i"}},
            {"name": {"$regex": query, "$options": "i"}}
        ]
    }).limit(5)

    matches = [{"_id": doc["_id"], "name": doc.get("name", "")} for doc in results]
    return jsonify({"status": "success", "matches": matches})

# 📈 Top gainers
@app.route('/top-gainers')
def top_gainers():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 5))
    docs = db["yahoo_gainers"].find().sort("change", -1).skip(offset).limit(limit)
    result = [{'_id': doc['_id'], 'price': doc['price'], 'change': doc['change']} for doc in docs]
    return jsonify(result)

# 📰 Analyse de sentiment (stockée)
@app.route('/analyze-sentiment')
def analyze_sentiment():
    news = list(db["news_articles"].find().sort("scraped_at", -1).limit(5))
    avg_doc = db["avg_sentiment"].find_one()
    avg_score = avg_doc.get("avg_sentiment_score", 0.0) if avg_doc else 0.0
    return jsonify({
        "news": [{"title": n["title"], "url": n["url"]} for n in news],
        "avg_score": avg_score
    })

# 🧪 Analyse de sentiment (locale)
@app.route('/analyze-news-local')
def analyze_news_local():
    try:
        news = list(db["news_articles"].find().sort("scraped_at", -1).limit(5))
        texts = [n["title"] for n in news]
        sentiment_pipeline = pipeline("sentiment-analysis", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
        results = sentiment_pipeline(texts)
        scores = [r['score'] if r['label'] == 'positive' else -r['score'] for r in results]
        avg_score = round(sum(scores) / len(scores), 4) if scores else 0.0
        return jsonify({
            "news": [{"title": n["title"], "url": n["url"]} for n in news],
            "avg_score": avg_score,
            "details": results
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🚀 Lancement local
if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
