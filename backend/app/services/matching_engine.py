import os
import pymupdf  # pip install pymupdf
from pydantic import BaseModel
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util
import torch
import json

# ==============================================================================
# 🧠 1. INITIALISATION DES MODÈLES (Chargé 1 seule fois au démarrage)
# ==============================================================================
print("⏳ Chargement du modèle NLP 'all-MiniLM-L6-v2' en mémoire...")
nlp_model = SentenceTransformer('all-MiniLM-L6-v2')

# Connexion à Ollama (Local)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" 
)

# Schéma JSON attendu par Qwen
class SkillsExtraction(BaseModel):
    found_skills: list[str]
    required_skills: list[str]

print("✅ Modèles prêts.")

# ==============================================================================
# 🛠️ 2. FONCTIONS UTILITAIRES (Extraction PDF)
# ==============================================================================
def extract_text_from_pdf(file_path: str) -> str:
    """Ouvre un fichier PDF local et extrait tout son texte."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier spécifié est introuvable : {file_path}")
    
    doc = pymupdf.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    
    return full_text

# ==============================================================================
# 🎯 3. FONCTION PRINCIPALE DE MATCHING
# ==============================================================================
def analyze_match(cv_file_path: str, job_description: str) -> dict:
    """
    Lit un CV PDF local, extrait les compétences via LLM puis calcule le score.
    """
    # --- ÉTAPE 0 : LECTURE DU FICHIER LOCAL ---
    print(f"📄 Lecture du fichier : {cv_file_path}...")
    try:
        cv_text = extract_text_from_pdf(cv_file_path)
    except Exception as e:
        return {"status": "error", "message": f"Erreur de lecture du PDF : {str(e)}"}

    if not cv_text.strip():
        return {"status": "error", "message": "Le PDF semble être vide ou illisible (ex: image scannée)."}

    # --- ÉTAPE 1 : EXTRACTION INTELLIGENTE (Qwen) ---
    print("🤖 Extraction des compétences avec Qwen...")
    system_prompt = """
    You are an HR expert. Your only mission is to extract technical and soft skill keywords.
    1. Find all the skills present in the provided CV text.
    2. Find all the skills required in the provided job description text.
    Do not write any sentences. Only fill out the requested JSON format.
    """
    
    user_prompt = f"--- CV TEXT ---\n{cv_text}\n\n--- JOB DESCRIPTION ---\n{job_description}"
    
    try:
        response = client.beta.chat.completions.parse(
            model="qwen2.5:3b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=SkillsExtraction, 
        )
        extracted_data = response.choices[0].message.parsed
        cv_skills = extracted_data.found_skills
        job_skills = extracted_data.required_skills
    except Exception as e:
        return {"status": "error", "message": f"Erreur avec le LLM Qwen : {str(e)}"}

    if not job_skills or not cv_skills:
        return {"status": "error", "message": "Impossible d'extraire les compétences des textes."}

    # --- ÉTAPE 2 : MATHS ET SCORING VECTORIEL ---
    print("🧮 Calcul du score de matching...")
    cv_embeddings = nlp_model.encode(cv_skills, convert_to_tensor=True)
    job_embeddings = nlp_model.encode(job_skills, convert_to_tensor=True)
    
    total_score = 0
    missing_skills = []
    
    cosine_scores = util.cos_sim(job_embeddings, cv_embeddings)
    
    for i, job_skill in enumerate(job_skills):
        best_match_score = torch.max(cosine_scores[i]).item()
        total_score += best_match_score
        
        # Si la similarité est < 40%, on considère la compétence manquante
        if best_match_score < 0.4:
            missing_skills.append(job_skill)
    
    final_match_score = round((total_score / len(job_skills)) * 100, 2)
    
    # --- ÉTAPE 3 : FORMATAGE DU RÉSULTAT ---
    return {
        "status": "success",
        "match_score": final_match_score,
        "data": {
            "cv_skills_found": cv_skills,
            "job_skills_required": job_skills,
            "missing_skills": missing_skills
        }
    }

# ==============================================================================
# 🧪 4. BLOC DE TEST
# ==============================================================================
if __name__ == "__main__":
    print("\n🚀 Lancement du test local...")
    
    # Remplacer par le chemin réel d'un CV sur ton PC !
    TEST_CV_PATH = "../../data/cv_sample_cleaned/moubarak_ezzyani.pdf" 
    
    
    TEST_JOB_DESC = """
Mastery of Python 3
Experience with SQL databases (PostgreSQL, SQLite)
Experience with Git, Docker, and CI/CD pipelines
Notions in Machine Learning (Pandas, Scikit-learn)
Team spirit
Good communication skills
"""
    
    # Sécurité pour le test : on vérifie que tu as bien modifié le chemin
    if os.path.exists(TEST_CV_PATH):
        resultat = analyze_match(TEST_CV_PATH, TEST_JOB_DESC)
        print("\n📊 RÉSULTAT DU MATCHING :")
        print(json.dumps(resultat, indent=4, ensure_ascii=False))
    else:
        print(f"\n⚠️ ERREUR : Tu dois d'abord modifier la variable TEST_CV_PATH (ligne {__import__('inspect').currentframe().f_lineno - 13}) pour pointer vers un vrai fichier PDF sur ton ordinateur.")