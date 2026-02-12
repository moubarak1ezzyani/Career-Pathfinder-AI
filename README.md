# 🚀 Career Pathfinder AI

**Career Pathfinder AI** est une plateforme intelligente conçue pour optimiser la préparation aux entretiens d'embauche. Elle combine le **Traitement du Langage Naturel (NLP)**, la **Génération Augmentée par Récupération (RAG)** et la **Vision par Ordinateur**.

## 🌟 Fonctionnalités Clés
- **📄 CV Scoring (NLP) :** Analyse sémantique et calcul de compatibilité (Cosine Similarity) entre un CV et une offre.
- **💬 Interview Coach (RAG) :** Chatbot contextuel (Groq/Llama3) qui simule un recruteur technique basé sur l'offre réelle.
- **👁️ Analyse Comportementale (Vision) :** Détection des émotions et du stress via webcam durant l'entretien (DeepFace).

## 🛠️ Stack Technique
- **Backend :** FastAPI, Python
- **Frontend :** React.js / Next.js 
- **AI/ML :** LangChain, ChromaDB, Sentence-Transformers, DeepFace

## 📂 Structure recommandée :

```plaintext
career-pathfinder-ai/
│
├── 📜 README.md              # Documentation du projet (votre intro, install, features)
├── 🐳 docker-compose.yml     # Orchestration (lance Backend + Frontend + DB ensemble)
├── 🙈 .gitignore             # Fichier très important (voir contenu plus bas)
│
├── 📂 backend/               # (FastAPI - Python)
│   ├── 📄 Dockerfile         # Pour conteneuriser l'API
│   ├── 📄 requirements.txt   # ou pyproject.toml (Dépendances Python)
│   ├── 📂 app/
│   │   ├── 🐍 main.py        # Point d'entrée (FastAPI init, CORS middleware)
│   │   ├── 📂 api/           # Les routes (Endpoints)
│   │   │   ├── 🐍 endpoints.py   # Routes: /upload, /chat, /analyze
│   │   │   └── 🐍 models.py      # Pydantic schemas (Request/Response format)
│   │   │
│   │   ├── 📂 core/          # Config
│   │   │   └── 🐍 config.py      # Variables d'env (Clés API Groq, Settings)
│   │   │
│   │   ├── 📂 services/      # 🧠 CŒUR DE L'IA (Logique métier)
│   │   │   ├── 🐍 pdf_parser.py     # [Data Sourcing] Extraction texte PDF
│   │   │   ├── 🐍 resume_matcher.py # [NLP] Calcul cosine similarity
│   │   │   ├── 🐍 rag_chain.py      # [RAG] LangChain + Groq logic
│   │   │   └── 🐍 video_analyzer.py # [Vision] DeepFace logic
│   │   │
│   │   └── 📂 utils/         # Fonctions utilitaires
│   │       └── 🐍 file_helpers.py   # Gestion des fichiers temporaires
│   │
│   ├── 📂 data/              # (Ignoré par git) Stockage local ChromaDB / Uploads
│   │   └── 📂 chromadb/      # Persistance de la base vectorielle
│   │
│   └── 📂 tests/             # [Qualité] Tests unitaires (pytest)
│       ├── 🐍 test_api.py
│       └── 🐍 test_services.py
│
├── 📂 frontend/              # (React ou Next.js)
│   ├── 📄 Dockerfile         # Pour conteneuriser le Front
│   ├── 📄 package.json       # Dépendances Node.js
│   ├── 📂 public/            # Assets statiques (Images, Icons)
│   └── 📂 src/
│       ├── 📂 components/    # Composants réutilisables
│       │   ├── ⚛️ Navbar.jsx
│       │   ├── ⚛️ UploadForm.jsx
│       │   └── ⚛️ ChatInterface.jsx
│       ├── 📂 pages/         # Routes (Next.js) ou Views (React)
│       │   ├── ⚛️ Dashboard.jsx
│       │   └── ⚛️ Interview.jsx
│       ├── 📂 services/      # Appels API vers le Backend
│       │   └── 📜 api.js     # Axios configuration (baseURL: http://localhost:8000)
│       └── 📜 App.jsx        # Main component
│
└── 📂 notebooks/             # [Exploration] Pour vos tests avant de coder l'app
    ├── 📓 01_data_cleaning.ipynb
    └── 📓 02_rag_prototyping.ipynb
```