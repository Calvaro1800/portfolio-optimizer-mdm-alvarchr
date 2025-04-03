# test_llm_advisor.py

from core.llm_advisor import generate_financial_advice, analyze_sentiment

print("🧪 Test #1 – Question au modèle Franklin")
question = "What is a good strategy for a low-risk investor in 2025?"
response = generate_financial_advice(question)
print(f"\n📨 Question:\n{question}")
print(f"\n🤖 Réponse du modèle:\n{response}")

print("\n🧪 Test #2 – Analyse de sentiment")
text = "The market showed strong gains today after tech stocks rallied."
sentiment_score = analyze_sentiment(text)
print(f"\n📰 Texte:\n{text}")
print(f"\n📊 Sentiment score: {sentiment_score:.3f}")