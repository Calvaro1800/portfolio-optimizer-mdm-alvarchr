import os
import torch
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# 🔐 Chargement des variables d’environnement (.env)
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# 🔎 Chargement du modèle de sentiment Hugging Face
SENTIMENT_MODEL = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL, token=HF_TOKEN)
model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL, token=HF_TOKEN)

# 🧠 Chargement du modèle GPT-2 (Otto)
generator = pipeline("text-generation", model="gpt2")

# 📈 Analyse des meilleurs gainers sur Yahoo Finance
def get_top_gainers(tickers: list, period="5d") -> list:
    data = yf.download(tickers, period=period, interval="1d", progress=False, auto_adjust=False)

    if isinstance(data.columns, pd.MultiIndex):
        if "Adj Close" not in data.columns.levels[0]:
            raise ValueError("❌ 'Adj Close' not found in multi-index data.")
        data = data["Adj Close"]
    else:
        if "Adj Close" not in data.columns:
            raise ValueError("❌ 'Adj Close' not found in Yahoo Finance data.")
        data = data["Adj Close"]

    returns = data.pct_change().sum().sort_values(ascending=False)
    return returns.head(5).index.tolist()

# 💡 Calcul simplifié du Sharpe Ratio
def calculate_sharpe_ratio(portfolio: dict, risk_free_rate=0.01) -> float:
    if not portfolio:
        return None

    tickers = list(portfolio.keys())
    weights = [portfolio[t] for t in tickers]
    total = sum(weights)
    weights = [w / total for w in weights]

    prices = yf.download(tickers, period="6mo", interval="1d", progress=False, auto_adjust=False)

    if isinstance(prices.columns, pd.MultiIndex):
        if "Adj Close" not in prices.columns.levels[0]:
            raise ValueError("❌ 'Adj Close' not found in multi-index data.")
        prices = prices["Adj Close"]
    else:
        if "Adj Close" not in prices.columns:
            raise ValueError("❌ 'Adj Close' not found in Yahoo Finance data.")
        prices = prices["Adj Close"]

    daily_returns = prices.pct_change().dropna()
    portfolio_returns = (daily_returns * weights).sum(axis=1)

    excess_returns = portfolio_returns - (risk_free_rate / 252)
    sharpe_ratio = excess_returns.mean() / excess_returns.std()
    return round(sharpe_ratio * (252**0.5), 2)

# 🧠 Otto – Conseiller IA (version GPT-2 locale)
def generate_financial_advice(
    question: str,
    sentiment_score: float = None,
    gainers_list: list = None,
    portfolio: dict = None,
    sharpe_value: float = None,
    transactions: str = ""
) -> str:
    if not question.strip():
        return "❗️Please enter a valid financial question so Otto can assist you."

    gainers = ', '.join(gainers_list[:5]) if gainers_list else "Not provided"
    portfolio_str = str(portfolio) if portfolio else "No current holdings"
    sentiment_str = (
        f"{sentiment_score:.2f} ({'positive' if sentiment_score > 0 else 'negative'})"
        if sentiment_score is not None else "Not provided"
    )
    sharpe_str = f"{sharpe_value:.2f}" if sharpe_value is not None else "Not provided"

    prompt = f"""
You are Otto, a senior portfolio strategist at a private bank. Your job is to give concise and professional advice to clients based on data.

Client's Question:
{question}

Data available:
- Market Sentiment Score: {sentiment_str}
- Top Gainers: {gainers}
- Client Portfolio: {portfolio_str}
- Recent Transactions: {transactions if transactions else "None"}
- Sharpe Ratio: {sharpe_str}

Respond in 2 to 4 sentences. Stay professional, helpful, and focused on the client’s goal.

Otto's answer:
""".strip()

    try:
        output = generator(prompt, max_length=250, num_return_sequences=1)[0]["generated_text"]
        answer = output.split("Otto's answer:")[-1].strip()
        return answer
    except Exception as e:
        return f"❌ Otto encountered an error: {e}"

# 📊 Analyse de sentiment
def analyze_sentiment(text: str) -> float:
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        scores = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
        return float(scores[1] - scores[0])
    except Exception as e:
        print(f"⚠️ Erreur d’analyse du sentiment: {e}")
        return 0.0

# 🧪 Test CLI
if __name__ == "__main__":
    news = "Investors are optimistic after the Fed signaled a pause in rate hikes."
    sentiment_score = analyze_sentiment(news)

    portfolio = {"AAPL": 10, "TSLA": 5, "NVDA": 3}
    transactions = "Bought 2 NVDA, Sold 1 TSLA"
    tickers_watchlist = list(portfolio.keys()) + ["MSFT", "GOOGL", "AMZN", "META"]
    gainers = get_top_gainers(tickers_watchlist)
    sharpe = calculate_sharpe_ratio(portfolio)

    question = "Should I rebalance my tech exposure now?"

    response = generate_financial_advice(
        question=question,
        sentiment_score=sentiment_score,
        gainers_list=gainers,
        portfolio=portfolio,
        sharpe_value=sharpe,
        transactions=transactions
    )

    print("🧠 Otto’s advice:\n", response)
