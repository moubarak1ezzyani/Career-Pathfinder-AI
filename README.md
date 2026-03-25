# 🚀 Career Pathfinder AI

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js Version](https://img.shields.io/badge/next.js-15+-black.svg)](https://nextjs.org/)
[![FastAPI Version](https://img.shields.io/badge/fastapi-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

**Career Pathfinder AI** est une plateforme intelligente de préparation aux entretiens d'embauche propulsée par l'Intelligence Artificielle. Elle permet d'analyser la compatibilité des CV, de s'entraîner via un simulateur d'entretien interactif et d'obtenir un feedback comportemental (émotions et stress) grâce à l'analyse vidéo.

---

## 🌟 Fonctionnalités Principales (Features)

- **📄 Analyse de CV & Matching AI** : Extraction automatique de texte (PDFPlumber) et calcul de similarité sémantique (Sentence-Transformers) entre votre profil et une offre d'emploi.
- **💬 Simulateur d'Entretien Interactif** : Génération de questions techniques personnalisées basées sur l'offre et votre CV, utilisant le modèle **Qwen 2.5** via Ollama.
- **👁️ Analyse de Performance Vidéo** : Détection des émotions dominantes et mesure du niveau de stress/confiance en temps réel via Webcam (**DeepFace** & **OpenCV**).
- **📊 Rapport de Progression** : Feedbacks détaillés, scores de match, et conseils IA pour améliorer vos prestations.
- **🐳 Architecture Conteneurisée** : Déploiement simplifié de l'ensemble de la stack (Frontend, Backend, DB) via Docker Compose.

---

## 🛠️ Stack Technique (Tech Stack)

### **Frontend**
- **Framework** : [Next.js 15+](https://nextjs.org/) (App Router)
- **Styling** : Vanilla CSS & Modern Design Patterns
- **Icons** : Lucide React

### **Backend**
- **Framework** : [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10)
- **ORM** : SQLAlchemy
- **Database** : PostgreSQL 15

### **Intelligence Artificielle**
- **LLM** : Qwen 2.5 (via [Ollama](https://ollama.com/))
- **Embeddings** : Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Computer Vision** : DeepFace, OpenCV, TensorFlow
- **NLP/Parsing** : PDFPlumber

### **DevOps**
- **Containerization** : Docker, Docker Compose

---

## 📋 Prérequis (Prerequisites)

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)
- [Ollama](https://ollama.com/) (installé sur la machine hôte pour faire tourner les modèles locaux)

---

## 🔑 Variables d'Environnement (Environment Variables)

Créez un fichier `.env` à la racine du projet en vous basant sur l'exemple suivant :

```env
# Database Configuration
DB_USER_env=postgres
DB_PASSWORD_env=votre_mot_de_passe
DB_HOST_env=db
DB_PORT_env=5432
DB_NAME_env=career_db

# Security
SECRET_KEY_env="votre_cle_secrete_ultra_longue"
ALGO_env="HS256"
TOKEN_EXPIRE_env=30

# AI Models Connectivity
OLLAMA_URL=http://host.docker.internal:11434/v1
```

---

## 🚀 Installation et Démarrage (Getting Started)

1. **Cloner le projet** :
   ```bash
   git clone https://github.com/votre-repo/career-pathfinder-ai.git
   cd career-pathfinder-ai
   ```

2. **Lancer Ollama** (Sur votre machine hôte) :
   ```bash
   ollama run qwen2.5:3b
   ```

3. **Démarrer avec Docker Compose** :
   ```bash
   docker-compose up --build -d
   ```

---

## 💻 Utilisation (Usage)

- **Application Web (Frontend)** : [http://localhost:3001](http://localhost:3001)
- **API Backend** : [http://localhost:8001](http://localhost:8001)
- **Documentation Interactive (SwaggerUI)** : [http://localhost:8001/docs](http://localhost:8001/docs)

---

## 📂 Structure du Projet (Détaillée)

```plaintext
Career-Pathfinder-AI/
├── 📂 backend/                  # Serveur FastAPI et services AI
│   ├── 📂 app/
│   │   ├── 📂 api/             # Modèles de données & Base de données
│   │   │   ├── 🐍 database.py   # Initialisation de SQLAlchemy & Connexion DB
│   │   │   ├── 🐍 models.py     # Définition des tables ORM (Candidats, CV, Match)
│   │   │   └── 🐍 schemas.py    # Modèles Pydantic pour l'entrée/sortie API
│   │   ├── 📂 core/            # Configuration et Sécurité
│   │   │   ├── 🐍 config.py     # Chargement des variables .env & Defaults
│   │   │   ├── 🐍 security.py   # Gestion JWT, Hashing de mots de passe
│   │   │   └── 🐍 prompts.py    # Centralisation des templates de prompts LLM
│   │   ├── 📂 services/       # Moteurs d'Intelligence Artificielle
│   │   │   ├── 🐍 matching_engine.py  # Calcul NLP de similarité CV/Offre
│   │   │   ├── 🐍 video_analyzer.py   # Traitement OpenCV & DeepFace (Émotions)
│   │   │   └── 🐍 document_parser.py  # Extraction de contenu PDF (PDFPlumber)
│   │   ├── 🐍 chatbot.py        # Logique de génération de quiz (Qwen 2.5)
│   │   └── 🐍 main.py           # Point d'entrée FastAPI & Définition des routes
│   ├── 📄 requirements.txt      # Liste des dépendances Python
│   └── 📄 Dockerfile            # Image Docker pour le Backend
├── 📂 frontend/                 # Interface Utilisateur Next.js
│   ├── 📂 app/
│   │   ├── 📂 context/         # Gestion d'état globale
│   │   │   └── ⚛️ AuthContext.tsx  # Contexte d'authentification utilisateur
│   │   ├── 📂 utils/           # Fonctions utilitaires
│   │   │   └── ⚛️ api.ts          # Client Fetch pré-configuré avec JWT
│   │   ├── 📂 login/           # Pages de connexion (Auth)
│   │   │   └── ⚛️ page.tsx
│   │   ├── 📂 register/        # Pages d'inscription (Auth)
│   │   │   └── ⚛️ page.tsx
│   │   ├── ⚛️ layout.tsx         # Squelette global & Polices (Inter)
│   │   ├── ⚛️ globals.css        # Styles CSS globaux
│   │   └── ⚛️ page.tsx           # Dashboard principal (Matching, Quiz & Vidéo)
│   ├── 📄 package.json          # Dépendances Node.js & Scripts
│   ├── 📄 next.config.ts        # Configuration du framework Next.js
│   └── 📄 Dockerfile            # Image Docker pour le Frontend
├── 📄 docker-compose.yml        # Orchestration (Postgres + Backend + Frontend)
└── 📄 .env                      # Configuration des clés et ports (local)
```

---

## 🔌 API Reference (Aperçu)

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `POST` | `/register` | Inscription d'un nouveau candidat |
| `POST` | `/login` | Authentification (retourne un JWT Token) |
| `POST` | `/analyze` | Analyse et Scoring du CV vs une Offre |
| `POST` | `/generate-quiz` | Génération des questions d'entretien |
| `POST` | `/evaluate-interview` | Évaluation des réponses du candidat |
| `POST` | `/analyze-video` | Analyse faciale (émotions/stress) de la vidéo |

---

## ⚖️ Licence et Auteurs

- **Auteur** : Moubarak EZ-ZYANI
- **Licence** : Ce projet est sous licence MIT.

---
*Projet réalisé dans le cadre du développement d'une solution IA complète pour l'orientation professionnelle.*