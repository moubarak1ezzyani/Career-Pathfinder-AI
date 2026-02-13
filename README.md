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
├── 📜 README.md
├── 🐳 docker-compose.yml
├── 🙈 .gitignore
│
├── 📂 backend/
│   ├── 📄 Dockerfile
│   ├── 📄 requirements.txt
│   ├── 📂 app/
│   │   ├── 🐍 main.py
│   │   ├── 📂 api/
│   │   │   ├── 🐍 endpoints.py      # Les 4 routes seront exposées ici
│   │   │   └── 🐍 models.py         # Schémas de données (Scores, Messages, Émotions)
│   │   │
│   │   ├── 📂 core/                 # Configuration (Groq, BDD)
│   │   │
│   │   ├── 📂 services/             # 🧠 TOUTE LA LOGIQUE MÉTIER
│   │   │   ├── 🐍 document_parser.py    # (Base) Extraction PDF
│   │   │   ├── 🐍 matching_engine.py    # (Route 1) Calcul de similarité CV/Offre
│   │   │   ├── 🐍 cover_letter_gen.py   # (Route 2) Génération par RAG
│   │   │   ├── 🐍 interview_chatbot.py  # (Route 3) Q&A LLM (Hard Skills)
│   │   │   └── 🐍 video_analyzer.py     # (Route 4) DeepFace (Soft Skills)
│   │   │
│   │   └── 📂 utils/
│   │       └── 🐍 file_helpers.py   # Gestion des fichiers temporaires
│   │
│   ├── 📂 data/
│   │   └── 📂 chromadb/
│   └── 📂 tests/
│       ├── 🐍 test_api.py
│       └── 🐍 test_services.py
│
├── 📂 frontend/
│   ├── 📄 package.json
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   │   ├── ⚛️ UploadArea.jsx
│   │   │   ├── ⚛️ ChatWindow.jsx        # Pour la Route 3
│   │   │   └── ⚛️ WebcamAnalyzer.jsx    # Composant prêt pour la Route 4
│   │   ├── 📂 pages/
│   │   │   ├── ⚛️ Dashboard.jsx         # Résultat Route 1 (Matching)
│   │   │   ├── ⚛️ ApplicationPrep.jsx   # Résultat Route 2 (Lettre)
│   │   │   └── ⚛️ Simulator.jsx         # Routes 3 & 4 combinées (Chat + Vidéo)
│   │   └── 📜 App.jsx
│
└── 📂 notebooks/
    ├── 📓 01_matching_logic.ipynb
    ├── 📓 02_rag_prompts.ipynb
    └── 📓 03_deepface_tests.ipynb
```

## branchs :
`
feature/route1-matching-engine (On remplit document_parser.py et matching_engine.py).

feature/route2-cover-letter (On remplit cover_letter_gen.py).

feature/route3-chatbot (On remplit interview_chatbot.py).

feature/route4-video-analysis (On remplit video_analyzer.py et on active le composant Webcam sur le Front).
`
***
## Cartographie du projet


### 📍 Le Point de Départ (Le Tronc Commun)

**Action Utilisateur :** "Upload a CV (PDF)"

* **Ce qui se passe en coulisse (Backend) :** Votre API (FastAPI) reçoit le PDF. Le script `pdf_parser.py` lit le texte, le découpe, et le transforme en vecteurs mathématiques (Embeddings) stockés dans votre base de données ChromaDB.
* **L'état de l'app :** L'IA "connaît" maintenant le candidat.

À partir de là, l'utilisateur a un menu devant lui et doit choisir sa Route.

---

### 🛣️ Route 1 : L'Audit de Carrière (Le cœur ML / MVP)

*L'objectif ici est de savoir si le candidat a le niveau pour un poste précis.*

* **L'action :** L'utilisateur colle le texte d'une "Offre d'Emploi de ses rêves" (Job Description) dans un champ texte.
* **La Machine :** L'IA vectorise cette offre et calcule la **similarité cosinus** entre le CV et l'offre.
* **Le Résultat Final (Dashboard) :**
* Un score global de compatibilité (ex: **78%**).
* Un "Gap Analysis" : Les compétences que le candidat possède vs celles qui lui manquent (ex: *"Il vous manque la compétence Docker demandée dans l'offre"*).



### 🛣️ Route 2 : L'Assistant Candidature (L'extension RAG n°1)

*L'objectif est d'accélérer la postulation.*

* **L'action :** L'utilisateur clique sur "Générer une lettre de motivation".
* **La Machine :** Le système prend le CV stocké, l'offre d'emploi, et les envoie au LLM (Groq/Llama3) avec un prompt strict : *"Agis comme ce candidat et rédige une lettre pour ce poste"*.
* **Le Résultat Final :** Un texte professionnel généré à l'écran, prêt à être copié/collé ou exporté en PDF.

### 🛣️ Route 3 : Le Simulateur d'Entretien Technique (L'extension RAG n°2)

*L'objectif est de s'entraîner aux "Hard Skills".*

* **L'action :** L'utilisateur lance un "Mock Interview" en mode Chat texte.
* **La Machine :** Le LLM analyse le CV et l'offre d'emploi, se met dans la peau du recruteur, et pose une question ciblée (ex: *"Je vois que vous avez fait du Python, comment géreriez-vous une API lente ?"*).
* **Le Résultat Final :** Une interface de Chatbot classique où l'utilisateur tape ses réponses et reçoit du feedback en direct.

### 🛣️ Route 4 : Le Crash-Test Multimodal (La Vision Future / Le "Wow Effect")

*C'est la version avancée de la Route 3, centrée sur les "Soft Skills".*

* **L'action :** L'utilisateur active sa webcam et son micro pour répondre aux questions de l'IA à l'oral.
* **La Machine :**
* Le son est converti en texte (Speech-to-Text).
* La vidéo est analysée en temps réel par **DeepFace** (capture des émotions et du regard).


* **Le Résultat Final :** Un rapport de fin d'entretien détaillant le niveau de stress, la confiance en soi perçue (analyse faciale), et la clarté de la communication (analyse textuelle).

---

### 🗺️ Résumé Visuel du Parcours (Arborescence)

```text
[ 📄 Upload du CV PDF ]  <-- Point de départ obligatoire
          |
          | (Choix de l'utilisateur sur l'interface)
          |
          +---> 1. "Est-ce que je matche ?" ---> [Matching Cosinus] ---> Jauge & Compétences manquantes
          |
          +---> 2. "Aide-moi à postuler"    ---> [RAG Texte]        ---> Lettre de motivation générée
          |
          +---> 3. "Entraîne-moi (Texte)"   ---> [RAG Chatbot]      ---> Chat interactif Q&A
          |
          +---> 4. "Entraîne-moi (Vidéo)"   ---> [Vision + RAG]     ---> Dashboard Stress & Soft Skills

```

### 💡 Mon conseil stratégique pour votre soutenance

Vous n'êtes **pas obligé** de faire les 4 routes parfaitement pour le 16 mars.
Si vous manquez de temps, la **Route 1** (Le Matching) et la **Route 3** (Le Chatbot) constituent déjà un projet d'ingénierie IA extrêmement solide et complet. La Route 4 est la "cerise sur le gâteau".

Voulez-vous qu'on choisisse ensemble quelles routes vous allez officiellement intégrer dans votre MVP (Produit Minimum Viable) pour garantir la réussite de votre présentation ?

## schéma de base de données
👤 1. Le Socle (Utilisateur & Données de base)

Table : users (Le candidat)

    id (UUID, Primary Key)

    email (String, Unique)

    name (String)

    created_at (Timestamp)

Table : resumes (Le CV uploadé)

    id (UUID, Primary Key)

    user_id (UUID, Foreign Key)

    file_path (String) -> Le chemin local où le PDF est sauvegardé.

    raw_text (Text) -> Le texte brut extrait du PDF.

    uploaded_at (Timestamp)

Table : job_targets (Les offres d'emploi ciblées)

    id (UUID, Primary Key)

    user_id (UUID, Foreign Key)

    title (String) -> Ex: "Développeur Python Junior"

    description_text (Text) -> Le texte collé par l'utilisateur.

    created_at (Timestamp)

🛣️ 2. Tables pour les Fonctionnalités (Les 4 Routes)

Table : match_results (Route 1 : L'Audit de Carrière)

    id (UUID, Primary Key)

    resume_id (UUID, Foreign Key)

    job_target_id (UUID, Foreign Key)

    overall_score (Float) -> Ex: 78.5 (%)

    missing_skills (JSON) -> Ex: ["Docker", "CI/CD", "AWS"]

    analyzed_at (Timestamp)

Table : cover_letters (Route 2 : L'Assistant Candidature)

    id (UUID, Primary Key)

    resume_id (UUID, Foreign Key)

    job_target_id (UUID, Foreign Key)

    generated_content (Text) -> La lettre rédigée par le LLM.

    created_at (Timestamp)

Table : interview_sessions (Routes 3 & 4 : Le Simulateur global)

    id (UUID, Primary Key)

    user_id (UUID, Foreign Key)

    job_target_id (UUID, Foreign Key) -> Pour savoir sur quel poste l'IA doit l'interroger.

    status (String) -> Ex: "in_progress", "completed"

    started_at (Timestamp)

    ended_at (Timestamp, Nullable)

Table : interview_messages (Route 3 : Historique du Chatbot)

    id (UUID, Primary Key)

    session_id (UUID, Foreign Key)

    sender (String) -> Doit être 'user' (candidat) ou 'ai' (recruteur).

    content (Text) -> Le texte du message.

    created_at (Timestamp)

Table : soft_skills_evaluations (Route 4 : Le rapport final DeepFace/Vidéo)

    id (UUID, Primary Key)

    session_id (UUID, Foreign Key)

    stress_score (Float) -> Calculé via DeepFace.

    confidence_score (Float)

    communication_score (Float) -> Calculé par le LLM sur la base des tics de langage.

    emotional_timeline (JSON) -> Ex: [{"time": "00:10", "emotion": "fear"}, ...] (Utile pour tracer un graphique sur le front-end à la fin).