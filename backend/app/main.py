# Libs
from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import pymupdf

# files imports
# from api.database import my_Base, engine
from app.services.matching_engine import analyze_match

# ------------------------------------
# my_Base.metada.create_all(bind=engine)
my_app = FastAPI(title="Career Pathfinder AI", version="1.0")

# check app
@my_app.get("/")
def read_root():
    return {"message":"Hello World"}


@my_app.post("/Register")
def sign_up():
    pass

@my_app.post("/Login")
def sign_in():
    pass


@my_app.post("/analyze")
async def perform_analysis(
    cv_file: UploadFile = File(...), 
    job_description: str = Form(...),
    required_skills: Optional[str] = Form(None)
):
    try:
        # 1. Vérification du format
        if not cv_file.filename.lower().endswith(".pdf"):
            raise ValueError("Le fichier fourni n'est pas un PDF.")

        # 2. Lecture du fichier PDF en mémoire
        pdf_content = await cv_file.read()
        cv_path="../data/cv_sample_cleaned/Data_Science/DS_1.pdf"
        doc = pymupdf.open(cv_path)    
        cv_text = ""
        for page in doc:    
            cv_text += page.get_text()

        # 3. Traitement des compétences (Conversion "python, sql" -> ["python", "sql"])
        skills_list = None
        if required_skills:
            # On découpe le texte avec les virgules et on enlève les espaces en trop
            skills_list = [skill.strip() for skill in required_skills.split(",")]

        # 4. Lancement de l'intelligence artificielle
        results = analyze_match(
            cv_text=cv_text,
            job_text=job_description,
            expected_skills=skills_list
        )
        
        return results

    except Exception as e:
        # Cela renverra l'erreur exacte à l'utilisateur pour comprendre ce qui cloche
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse : {str(e)}")