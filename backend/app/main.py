from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from openai import OpenAI
import pymupdf
from sentence_transformers import SentenceTransformer
import torch
from sentence_transformers import util

app = FastAPI()

# 1. Chargement de notre modèle de calcul mathématique (le NLP léger)
nlp_model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Configuration du "Moule" JSON (Structured Output)
class SkillsExtraction(BaseModel):
    found_skills: list[str]
    required_skills: list[str]

# 3. Connexion à votre Qwen 3.5 local via Ollama
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" # La clé n'a pas d'importance en local
)

@app.post("/analyze")
async def analyze_cv(file: UploadFile = File(...), job_description: str = Form(...)):
    # --- PHASE 1 : LECTURE DU PDF ---
    pdf_content = await file.read()
    doc = pymupdf.open(stream=pdf_content, filetype="pdf")
    cv_text = ""
    for page in doc:
        cv_text += page.get_text()
    
    # --- PHASE 2 : EXTRACTION INTELLIGENTE PAR QWEN 3.5 ---
    prompt_systeme = """
    Tu es un expert en recrutement très strict. Ta seule mission est d'extraire les mots-clés de compétences techniques et soft skills.
    1. Trouve toutes les compétences présentes dans le texte du CV fourni.
    2. Trouve toutes les compétences exigées dans le texte de l'offre d'emploi fournie.
    Ne rédige aucune phrase. Remplis uniquement le format JSON demandé.
    """
    
    prompt_utilisateur = f"--- TEXTE DU CV ---\n{cv_text}\n\n--- TEXTE DE L'OFFRE ---\n{job_description}"

    # Appel au modèle local Qwen 3.5 via Ollama
    response = client.beta.chat.completions.parse(
        model="qwen2.5:3b", # Le nom exact du modèle sur Ollama
        messages=[
            {"role": "system", "content": prompt_systeme},
            {"role": "user", "content": prompt_utilisateur}
        ],
        response_format=SkillsExtraction, # C'est ici qu'on force le JSON Pydantic !
    )

    extracted_data = response.choices[0].message.parsed
    cv_skills = extracted_data.found_skills
    job_skills = extracted_data.required_skills

    # --- PHASE 3 : MATCHING SÉMANTIQUE ---
    # S'il n'y a pas de compétences requises, on évite les erreurs de division par zéro
    if not job_skills or not cv_skills:
        return {"status": "error", "message": "Impossible d'extraire les compétences."}

    # Transformation des mots en vecteurs mathématiques
    cv_embeddings = nlp_model.encode(cv_skills, convert_to_tensor=True)
    job_embeddings = nlp_model.encode(job_skills, convert_to_tensor=True)

    # Calcul du score global
    # (On compare chaque compétence requise avec toutes les compétences du CV pour trouver la meilleure correspondance)
    total_score = 0
    missing_skills = []

    
    cosine_scores = util.cos_sim(job_embeddings, cv_embeddings)

    for i, job_skill in enumerate(job_skills):
        # On cherche le score maximum pour cette compétence requise
        best_match_score = torch.max(cosine_scores[i]).item()
        total_score += best_match_score
        
        # Si le score de similarité est trop faible (ex: < 0.4), on considère la compétence comme manquante
        if best_match_score < 0.4:
            missing_skills.append(job_skill)

    # Moyenne sur 100
    final_match_score = (total_score / len(job_skills)) * 100

    return {
        "status": "success",
        "match_score": round(final_match_score, 2),
        "data": {
            "cv_skills_found": cv_skills,
            "job_skills_required": job_skills,
            "missing_skills": missing_skills
        }
    }


# ------------------------------------
# my_Base.metada.create_all(bind=engine)
# my_app = FastAPI(title="Career Pathfinder AI", version="1.0")

# # check app
# @my_app.get("/")
# def read_root():
#     return {"message":"Hello World"}


# @my_app.post("/Register")
# def sign_up():
#     pass

# @my_app.post("/Login")
# def sign_in():
#     pass