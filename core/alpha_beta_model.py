# core/alpha_beta_model.py

from core.regression_model import predict_price
from core.portfolio_utils import load_cleaned_data
from core.classifier import classify_sharpe

import pandas as pd
import numpy as np

# 🇫🇷 Calcul du Sharpe Ratio avec taux sans risque fixe
# 🇩🇪 Sharpe-Ratio-Berechnung mit festem risikofreiem Zinssatz
# 🇬🇧 Sharpe ratio computation with fixed risk-free rate
def compute_sharpe_ratio(predicted, price, performance, risk_free_rate=0.02):
    returns = predicted / price - 1
    volatility = performance.abs() + 1e-6  # 🇫🇷 éviter division par zéro / 🇩🇪 Division durch Null vermeiden / 🇬🇧 avoid division by zero
    sharpe = (returns - risk_free_rate) / volatility
    return sharpe


# 🇫🇷 Calcule les scores alpha et beta pour chaque actif
# 🇩🇪 Berechnet Alpha- und Beta-Scores für jeden Titel
# 🇬🇧 Computes alpha and beta scores for each asset
def score_alpha_beta(df, predicted_returns):
    if df is None or predicted_returns is None:
        return None

    # ✨ Transformation explicite en vecteur 1D
    if isinstance(predicted_returns, pd.DataFrame):
        predicted_returns = predicted_returns.values.ravel()
    elif hasattr(predicted_returns, "flatten"):
        predicted_returns = predicted_returns.flatten()

    df["predicted_return"] = predicted_returns
    df["alpha"] = df["predicted_return"] - df["performance"]  # 🇫🇷 rendement excessif
    df["beta"] = df["performance"].rolling(3, min_periods=1).std()  # 🇬🇧 rolling std = beta proxy

    return df


# 🇫🇷 Filtre les meilleures actions selon les seuils alpha/beta
# 🇩🇪 Filtert Top-Aktien basierend auf Alpha/Beta-Schwellen
# 🇬🇧 Filters best stocks based on alpha/beta thresholds
def filter_top_assets(df, alpha_min=0.5, beta_max=2.0):
    return df[(df["alpha"] > alpha_min) & (df["beta"] < beta_max)]


# 🇫🇷 Pipeline complet : chargement, prédiction, scoring, sélection
# 🇩🇪 Gesamtpipeline: Laden, Vorhersage, Bewertung, Auswahl
# 🇬🇧 Full pipeline: loading, prediction, scoring, filtering
def alpha_beta_pipeline():
    print("🚀 Lancement du pipeline Alpha-Beta + Sharpe...\n")

    print("[📥] Chargement des données MongoDB…")
    df = load_cleaned_data()
    print(df.head())

    print("\n[🤖] Prédiction IA des rendements futurs…")
    predicted = predict_price(df)

    print("\n[📊] Calcul des scores alpha / beta…")
    df_scored = score_alpha_beta(df, predicted)

    print("\n[⚖️] Calcul du Sharpe Ratio…")
    df_scored["sharpe_ratio"] = compute_sharpe_ratio(
        df_scored["predicted_return"],
        df_scored["price"],
        df_scored["performance"]
    )

    print("\n[🔍] Interprétation qualitative du Sharpe Ratio…")
    df_scored["label"] = df_scored["sharpe_ratio"].apply(classify_sharpe)

    print("\n[✅] Filtrage des meilleures opportunités…")
    top_assets = filter_top_assets(df_scored)

    return df_scored, top_assets
