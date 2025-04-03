from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch

# Chargement du modèle pré-entraîné depuis Hugging Face
MODEL_NAME = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)
model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME)

# Labels possibles
LABELS = ["negative", "neutral", "positive"]

def predict_sentiment(text):
    """
    🇫🇷 Analyse le sentiment d'un texte financier.
    🇩🇪 Sentimentanalyse eines Textes mit RoBERTa-Modell.
    🇬🇧 Returns label and score for sentiment (negative/neutral/positive).
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
    return {
        "label": LABELS[predicted_class],
        "score": round(probabilities[0][predicted_class].item(), 4)
    }

