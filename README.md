# 📊 Portfolio Optimizer — alvarchr — MDM FS2025

Ein Projekt gemacht für das Modul **Model Deployment & Maintenance** an der ZHAW (Frühsemester 2025).  
👤 Name: alvarchr  
📘 Modul: MDM FS2025  
🎓 Betreuer: Prof. Adrian Moser

---
Willkommen zu meinem Projekt **Portfolio Optimizer mit KI**, das ich im Rahmen des Moduls *Model Deployment & Maintenance (MDM)* an der ZHAW entwickelt habe. Dieses Projekt war wirklich eine Reise – mit vielen Herausforderungen, Frustmomenten, aber auch viel Lernen und Stolz am Ende!

## 🎯 Ziel des Projekts

Ich wollte in diesem Projekt ein **echtes Finanz-Tool** machen:  
Ein Portfolio Optimizer mit **KI**, der echte Aktien-Daten benutzt, Empfehlungen gibt, und sogar **wie ein Finanzberater sprechen kann**.

Am Anfang hatte ich **null Erfahrung** mit Python, MongoDB, APIs oder Flask.  
Es war wirklich eine **Herausforderung**, aber ich habe **Schritt für Schritt alles gelernt**, manchmal mit Hilfe von ChatGPT, Google, Fehlern, und viele, viele Tests...

---

## 🧩 Funktionen (übersicht)

| Kategorie                | Funktion                                                                 |
|--------------------------|--------------------------------------------------------------------------|
| 📈 Scraping              | Aktienkurse automatisch holen (Top Gainers) von Yahoo Finance            |
| 📰 News & Sentiment      | Finanznachrichten scrapen und mit Sentiment-Modell analysieren           |
| 📉 Regression IA         | ML-Modell sagt die Performance von Aktien voraus                         |
| 🧠 LLM Finanzberater     | Ein lokales GPT-2 Modell antwortet auf Portfolio-Fragen                   |
| 📊 Sharpe Ratio          | Berechnet das Risiko-Rendite-Verhältnis vom Portfolio                    |
| 🧑‍💻 Flask UI            | Webseite mit Datei-Upload, Aktien-Suche, Charts und IA-Formular           |
| 📅 Termin vereinbaren    | Benutzer kann einen virtuellen Finanzberater wählen & Bild anzeigen lassen |
| ⏰ Automatisierung        | Daten-Updates mit CRON (täglich 10:00 und 18:00)                         |
| 🧪 Unit Tests            | `pytest`-Skripte für Scraping, ML, LLM, Sentiment usw.                   |
| 🐳 Docker                | Containerisierung bereit (lokale Ausführung, Deployment geplant)         |


## 🧠 Meine Learnings

Ich komme nicht aus einem technischen Hintergrund – ehrlich gesagt war das mein erstes richtiges Python-Projekt. Ich hatte viele Herausforderungen:

- Ich musste zuerst lernen, wie man **mit MongoDB arbeitet** (IP-Ranges, Authentifizierung, Compass-Probleme).
- Dann kam der **Scraping-Teil**, der viel schwieriger war als gedacht (Playwright war ein Albtraum... danke BeautifulSoup).
- Das Modelltraining war auch nicht leicht – ich musste herausfinden, wie man **Modelle lädt, testet und Metriken ausrechnet**.
- Flask war neu für mich, aber ich habe geschafft, eine schöne UI zu bauen, sogar mit **Diagrammen und Autocomplete-Feldern**!
- Und GitHub Actions... naja, das war Trial & Error 😅

Trotzdem habe ich nicht aufgegeben – und ich bin sehr stolz auf mein Ergebnis!

---

## 🧪 Tests & Qualität

Ich habe viele Tests geschrieben, z.B.:

- `test_models.py` → Testet Sharpe Ratio, Klassifikation & Regression
- `test_sentiment.py` → Sentiment-Analyse funktioniert richtig
- `test_update_all_stocks.py` → Datenimport von allen Symbolen
- `test_ask_model.py` → LLM-Antworten korrekt formatiert
Ausserdem:
- `debug_llm.py` → Zum Testen meines lokalen LLMs
- `compute_avg_sentiment.py` → Aggregation der Sentimentwerte

## 📂 Projektstruktur

```bash
projekt1-python/
│
├── app.py                     # Haupt-Flask-App
├── core/                      # ML-Modelle: Regressor, LLM, Sharpe utils
├── static/, templates/        # UI (HTML, CSS, JS, Charts)
├── update_gainers.py          # Scraping-Skript für Yahoo Finance
├── update_news.py             # News-Scraping
├── analyze_sentiment.py       # Sentimentanalyse
├── compute_avg_sentiment.py   # Durchschnitt berechnen
├── uploads/                   # Uploads von CSV
├── logs/, models/, images/    # Lokale Logs & Modelle
└── .env, requirements.txt     # Konfiguration & Install

🎓 Fazit
Dieses Projekt war nicht nur eine akademische Aufgabe – es war meine persönliche Herausforderung. Ich habe gelernt, wie man:

sauberen Python-Code schreibt

mit echten Daten umgeht

ein UI baut

Modelle versteht & integriert

Fehler debuggt (viele davon...)

Ich bin stolz, das geschafft zu haben. 💪

Merci fürs Lesen – und ich hoffe, mein Projekt zeigt, wie viel Mühe ich reingesteckt habe!
Falls du mein Portfolio optimieren willst... frag einfach mein Modell 😄