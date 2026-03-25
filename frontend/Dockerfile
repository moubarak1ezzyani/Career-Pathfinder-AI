# Utiliser une image Node.js compatible avec Next.js 16+ (Node 20+)
FROM node:20-alpine


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

# Lancer l'application en mode développement
CMD ["npm", "run", "dev", "--", "-p", "3001"]

# Construire l'image (Build) : <sudo docker build -t career-pathfinder-frontend .>
# Lancer le conteneur (Run) : <sudo docker run -d -p 3001:3001 --name frontend-app career-pathfinder-frontend>