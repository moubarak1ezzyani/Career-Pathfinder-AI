import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any

# ==============================================================================
# 🧠 CHARGEMENT DU MODÈLE EN MÉMOIRE (Exécuté 1 seule fois au démarrage)
# ==============================================================================
print("⏳ Chargement du modèle NLP 'all-MiniLM-L6-v2' en mémoire...")
# Cette variable globale sera réutilisée par la fonction analyze_match
NLP_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Modèle NLP chargé avec succès !")


# ==============================================================================
# 🛠️ FONCTIONS UTILITAIRES
# ==============================================================================
def clean_text(text: str) -> str:
    """
    Nettoie le texte brut (minuscules, retrait de la ponctuation).
    """
    if not text:
        return ""
    # Remplacer les retours à la ligne et espaces multiples par un seul espace
    text = re.sub(r'\s+', ' ', text)
    # Ne garder que les caractères alphanumériques et les espaces
    text = re.sub(r'[^\w\s]', ' ', text)
    return text.lower().strip()


# ==============================================================================
# 🎯 FONCTION PRINCIPALE (Appelée par l'API)
# ==============================================================================
def analyze_match(cv_text: str, job_text: str, expected_skills: List[str] = None) -> Dict[str, Any]:
    """
    Compare le CV et l'offre d'emploi.
    Retourne un dictionnaire (prêt à être converti en JSON par FastAPI).
    """
    # 1. Nettoyage des textes
    cv_clean = clean_text(cv_text)
    job_clean = clean_text(job_text)

    # 2. Vectorisation (Embeddings) en utilisant le modèle global NLP_MODEL
    # .reshape(1, -1) est requis par scikit-learn pour comparer des vecteurs uniques
    cv_embedding = NLP_MODEL.encode(cv_clean).reshape(1, -1)
    job_embedding = NLP_MODEL.encode(job_clean).reshape(1, -1)

    # 3. Calcul du Score (Cosine Similarity)
    similarity_matrix = cosine_similarity(cv_embedding, job_embedding)
    # On extrait le score, on le met sur 100 et on arrondit à 2 décimales
    match_score = round(similarity_matrix[0][0] * 100, 2)

    # 4. Gap Analysis (Recherche des compétences manquantes)
    # Si aucune liste n'est fournie, on utilise une liste par défaut (MVP)
    if expected_skills is None:
        expected_skills = [
            "python", "fastapi", "django", "sql", "postgresql", 
            "sqlite", "git", "docker", "ci", "cd", 
            "machine learning", "pandas", "scikit-learn"
        ]

    found_skills = []
    missing_skills = []

    for skill in expected_skills:
        # On cherche le mot-clé en minuscules dans le CV nettoyé
        if skill.lower() in cv_clean:
            found_skills.append(skill)
        else:
            missing_skills.append(skill)

    # 5. Retour du résultat formaté
    return {
        "match_score": match_score,
        "gap_analysis": {
            "found_skills": found_skills,
            "missing_skills": missing_skills
        }
    }