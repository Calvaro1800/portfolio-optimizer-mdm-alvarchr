"""
🇫🇷 Module pour classifier le Sharpe Ratio selon des niveaux de performance.
🇩🇪 Modul zur Klassifizierung des Sharpe-Verhältnisses nach Performance-Niveaus.
🇬🇧 Module to classify Sharpe Ratio into performance levels.
"""

def classify_sharpe(sharpe_ratio):
    """
    🇫🇷 Retourne une étiquette qualitative selon le Sharpe Ratio.
    🇩🇪 Gibt ein qualitatives Label basierend auf dem Sharpe-Verhältnis zurück.
    🇬🇧 Returns a qualitative label based on Sharpe Ratio.
    """
    if sharpe_ratio < 0:
        return "⚠️ Négatif — Risque excessif pour retour négatif"
    elif sharpe_ratio < 0.5:
        return "🔴 Faible — Retour insuffisant pour le niveau de risque"
    elif sharpe_ratio < 1.0:
        return "🟠 Modéré — Acceptable mais pas optimal"
    elif sharpe_ratio < 1.5:
        return "🟢 Bon — Bonne efficacité rendement/risque"
    else:
        return "🟣 Excellent — Portefeuille très performant"

# 🔎 Exemple d'utilisation
if __name__ == "__main__":
    ratios = [-0.5, 0.3, 0.9, 1.2, 1.8]
    for r in ratios:
        label = classify_sharpe(r)
        print(f"Sharpe Ratio = {r:.2f} → {label}")
