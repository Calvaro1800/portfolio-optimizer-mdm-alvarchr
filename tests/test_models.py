# test_models.py

import unittest
import os
import re
from pymongo import MongoClient
from core.portfolio_utils import load_cleaned_data
from core.classifier import classify_sharpe
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class TestMongoPipeline(unittest.TestCase):
    def test_load_cleaned_data(self):
        """
        🇫🇷 Vérifie que la fonction load_cleaned_data() retourne un DataFrame non vide avec les bonnes colonnes.
        🇩🇪 Prüft, ob load_cleaned_data() ein DataFrame mit den erwarteten Spalten zurückgibt.
        🇬🇧 Checks that load_cleaned_data() returns a non-empty DataFrame with expected columns.
        """
        df = load_cleaned_data()

        self.assertIsNotNone(df, "Le DataFrame retourné est None")
        self.assertFalse(df.empty, "Le DataFrame est vide — vérifier MongoDB")
        self.assertIn("price", df.columns, "Colonne 'price' absente")
        self.assertIn("performance", df.columns, "Colonne 'performance' absente")

        print("[✅] Test load_cleaned_data OK")

class TestClassifier(unittest.TestCase):
    def test_classify_sharpe(self):
        """
        🇫🇷 Vérifie la classification du Sharpe Ratio en catégories textuelles.
        🇩🇪 Testet die Einteilung des Sharpe-Verhältnisses in Kategorien.
        🇬🇧 Tests Sharpe Ratio classification logic.
        """
        self.assertEqual(classify_sharpe(-0.5), "⚠️ Négatif — Risque excessif pour retour négatif")
        self.assertEqual(classify_sharpe(0.2), "🔴 Faible — Retour insuffisant pour le niveau de risque")
        self.assertEqual(classify_sharpe(0.8), "🟠 Modéré — Acceptable mais pas optimal")
        self.assertEqual(classify_sharpe(1.2), "🟢 Bon — Bonne efficacité rendement/risque")
        self.assertEqual(classify_sharpe(1.8), "🟣 Excellent — Portefeuille très performant")

        print("[✅] Test classify_sharpe OK")

class TestAllStocksCollection(unittest.TestCase):
    def test_yahoo_all_stocks_collection(self):
        """
        🇫🇷 Vérifie que la collection 'yahoo_all_stocks' contient bien des documents avec les bons champs et types.
        🇩🇪 Prüft, ob 'yahoo_all_stocks' Dokumente mit den erwarteten Feldern enthält.
        🇬🇧 Checks that 'yahoo_all_stocks' has documents with expected fields and types.
        """
        mongo_uri = os.getenv("MONGO_URI")
        self.assertIsNotNone(mongo_uri, "❌ MONGO_URI non trouvé dans .env")

        client = MongoClient(mongo_uri)
        db = client["gainers_db"]
        collection = db["yahoo_all_stocks"]

        docs = list(collection.find().limit(5))
        self.assertGreater(len(docs), 0, "❌ Aucun document trouvé dans 'yahoo_all_stocks'")

        example = docs[0]
        self.assertIn("_id", example)
        self.assertIn("name", example)
        self.assertIn("price", example)
        self.assertIn("change", example)
        self.assertIn("percent_change", example)
        self.assertIn("volume", example)
        self.assertIn("scraped_at", example)

        self.assertIsInstance(example["_id"], str)
        self.assertIsInstance(example["name"], str)
        self.assertIsInstance(example["price"], float)
        self.assertIsInstance(example["change"], float)
        self.assertIsInstance(example["percent_change"], float)
        self.assertIsInstance(example["volume"], int)

        print(f"[✅] Exemple document : {example}")
        print("[✅] Test yahoo_all_stocks OK")
        client.close()

class TestSymbolExtractionAndPrice(unittest.TestCase):
    def test_symbol_extraction_and_price_lookup(self):
        """
        🇫🇷 Teste l'extraction du symbole depuis une question IA et la récupération du prix depuis MongoDB.
        🇩🇪 Testet die Extraktion eines Symbols aus einer Frage und die Preisanfrage aus MongoDB.
        🇬🇧 Tests symbol extraction from question and price lookup in MongoDB.
        """
        mongo_uri = os.getenv("MONGO_URI")
        self.assertIsNotNone(mongo_uri)

        client = MongoClient(mongo_uri)
        db = client["gainers_db"]
        collection = db["yahoo_all_stocks"]

        question = "What is the prediction for NVDA?"
        match = re.search(r"for (\w+)", question)
        self.assertIsNotNone(match, "❌ Aucun symbole extrait de la question.")
        symbol = match.group(1).upper()

        doc = collection.find_one({"_id": symbol})
        self.assertIsNotNone(doc, f"❌ Aucun document trouvé pour le symbole {symbol}")
        self.assertIn("price", doc)
        self.assertIsInstance(doc["price"], float)

        print(f"[✅] Symbole extrait : {symbol}")
        print(f"[✅] Prix trouvé : {doc['price']}")
        client.close()

if __name__ == "__main__":
    unittest.main()
