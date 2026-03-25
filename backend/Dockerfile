# Utiliser une image Python officielle légère
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /backend

# Installer les dépendances système nécessaires (ex: pour compiler certains packages ou psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier de dépendances en premier (optimisation du cache Docker)
COPY requirements.txt .

# Installer les dépendances Python
# On force la version CPU de PyTorch (utilisée par sentence-transformers) pour alléger l'image
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY . .

# Exposer le port sur lequel FastAPI va tourner
EXPOSE 8001

# Commande pour démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]


# Construire l'image Docker (ça peut prendre quelques minutes la première fois) :

# <docker build -t career-pathfinder-backend .>
# -----------------------------------------------
# Démarrer le conteneur :

# <docker run -d -p 8001:8001 --name backend-ai career-pathfinder-backend>    
