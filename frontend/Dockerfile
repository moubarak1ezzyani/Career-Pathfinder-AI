# Utiliser une image Node.js légère
FROM node:18-alpine

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY package.json package-lock.json* ./

# Installer les dépendances
RUN npm install

# Copier le reste du code du frontend
COPY . .

# Exposer le port 3001 (celui que tu utilises)
EXPOSE 3001

# Lancer l'application en mode développement (pratique pour voir les changements en direct)
# Si tu veux la production, remplace par : RUN npm run build CMD ["npm", "start"]
CMD ["npm", "run", "dev", "-p", "3001"]