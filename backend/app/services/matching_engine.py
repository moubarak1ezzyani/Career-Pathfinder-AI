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
# 🛠️ 2. FONCTION PRINCIPALE DE MATCHING
# ==============================================================================
def analyze_match(cv_text: str, job_description: str) -> dict:
    """
    Extrait les compétences via LLM puis calcule un score de similarité vectorielle.
    """
    # --- ÉTAPE 1 : EXTRACTION INTELLIGENTE (Qwen) ---
    system_prompt = """
    You are an HR expert. Your only mission is to extract technical and soft skill keywords.
    1. Find all the skills present in the provided CV text.
    2. Find all the skills required in the provided job description text.
    Do not write any sentences. Only fill out the requested JSON format.
    """
    
    user_prompt = f"--- CV TEXT ---\n{cv_text}\n\n--- JOB DESCRIPTION ---\n{job_description}"
    
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

    # Sécurité si le LLM n'a rien trouvé
    if not job_skills or not cv_skills:
        return {
            "status": "error", 
            "message": "Impossible d'extraire les compétences des textes fournis."
        }

    # --- ÉTAPE 2 : MATHS ET SCORING VECTORIEL ---
    cv_embeddings = nlp_model.encode(cv_skills, convert_to_tensor=True)
    job_embeddings = nlp_model.encode(job_skills, convert_to_tensor=True)
    
    total_score = 0
    missing_skills = []
    
    # Calcul de la matrice de similarité Cosinus
    cosine_scores = util.cos_sim(job_embeddings, cv_embeddings)
    
    for i, job_skill in enumerate(job_skills):
        best_match_score = torch.max(cosine_scores[i]).item()
        total_score += best_match_score
        
        # Si la similarité est < 40% (0.4), on considère la compétence manquante
        if best_match_score < 0.4:
            missing_skills.append(job_skill)
    
    # Calcul du score final sur 100
    final_match_score = round((total_score / len(job_skills)) * 100, 2)
    
    # --- ÉTAPE 3 : FORMATAGE DU RÉSULTAT ---
    final_result = {
        "status": "success",
        "match_score": final_match_score,
        "data": {
            "cv_skills_found": cv_skills,
            "job_skills_required": job_skills,
            "missing_skills": missing_skills
        }
    }
    
    return final_result

# ==============================================================================
# 🧪 3. BLOC DE TEST (Exécuté uniquement si on lance ce fichier directement)
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Lancement du test rapide...")
    test_cv_text = "Développeur avec 3 ans d'expérience en Python, FastAPI, Docker et bases de données SQL."
    test_job_text = "Recherche dev Python 3. Doit maîtriser SQL, Git, Docker et Next.js."
    
    resultat = analyze_match(test_cv_text, test_job_text)
    print("\n📊 RÉSULTAT DU MATCHING :")
    print(json.dumps(resultat, indent=4, ensure_ascii=False))