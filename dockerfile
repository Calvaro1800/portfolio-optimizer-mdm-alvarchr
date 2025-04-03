# 📦 Étape 1 : Image de base légère et compatible avec llama-cpp-python
FROM python:3.12-slim

# 📁 Étape 2 : Répertoire de travail
WORKDIR /app

# 📄 Étape 3 : Copier tous les fichiers dans le conteneur
COPY . .

# ⚙️ Étape 4 : Installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    cmake \
    make \
    libffi-dev \
    libsasl2-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    build-essential \
    python3-dev \
    git \
    curl && \
    rm -rf /var/lib/apt/lists/*

# 🔧 Étape 5 : Mise à jour de pip
RUN pip install --upgrade pip

# 📜 Étape 6 : Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# 🔐 Étape 7 : Charger les variables d’environnement depuis .env automatiquement
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV GGUF_MODEL_PATH=/app/models/llama-model.gguf

# ✅ Option : copie explicite du modèle si tu le montes à l’extérieur
# COPY models/llama-model.gguf /app/models/llama-model.gguf

# 🌍 Étape 8 : Exposer le port Flask
EXPOSE 5000

# 🚀 Étape 9 : Lancement de l’app Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
