import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Importation de tes modules de Base de Données
from api.database import get_db, engine
import models

# Importation de tes moteurs d'IA (les fichiers qu'on a nettoyés !)
from matching_engine import analyze_match
from chatbot import generate_questions, evaluate_candidate, QuestionList

# Création des tables dans la base de données (si elles n'existent pas)
models.my_Base.metadata.create_all(bind=engine)

app = FastAPI(title="Career Pathfinder AI", version="1.0")

# --- CORS CONFIG ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dossier local pour sauvegarder les CV uploadés
UPLOAD_DIR = "uploads/cvs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==========================================
# PYDANTIC SCHEMAS (Pour la validation des requêtes)
# ==========================================
class EvaluateInterviewRequest(BaseModel):
    session_id: int
    candidate_answers: dict[int, str]

# ==========================================
# ROUTES (Endpoints)
# ==========================================

# --- 1. CV Analysis Route ---
@app.post("/analyze")
async def analyze_cv(
    file: UploadFile = File(...), 
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Sauvegarder physiquement le fichier PDF
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Créer un candidat "Démo" pour l'instant (à lier à ton auth plus tard)
    candidat = models.Candidat(name="User Démo", email="demo@test.com")
    db.add(candidat)
    db.commit()
    db.refresh(candidat)

    # 3. Enregistrer le Resume et le JobTarget en DB
    resume = models.Resume(candidat_id=candidat.id, file_path=file_location)
    job_target = models.JobTarget(candidat_id=candidat.id, description_text=job_description)
    db.add(resume)
    db.add(job_target)
    db.commit()
    db.refresh(resume)
    db.refresh(job_target)

    # 4. Appeler ton super moteur d'IA
    result = analyze_match(cv_file_path=file_location, job_description=job_description)

    if result["status"] == "success":
        # 5. Sauvegarder les résultats du Match en DB
        match_result = models.MatchResults(
            resume_id=resume.id,
            job_target_id=job_target.id,
            overall_score=result["match_score"],
            match_details=result["data"]
        )
        db.add(match_result)
        db.commit()

    return {
        "candidat_id": candidat.id,
        "job_target_id": job_target.id,
        "ai_result": result
    }

# --- 2. Generate Interview Questions Route ---
@app.post("/generate-quiz")
async def generate_quiz(job_target_id: int = Form(...), db: Session = Depends(get_db)):
    
    # 1. Récupérer l'offre d'emploi depuis la base de données
    job_target = db.query(models.JobTarget).filter(models.JobTarget.id == job_target_id).first()
    if not job_target:
        raise HTTPException(status_code=404, detail="Offre d'emploi introuvable")

    # 2. Appeler l'IA (Qwen via chatbot.py)
    quiz = generate_questions(job_target.description_text)
    
    # 3. Créer une session d'interview en base de données
    session = models.InterviewSession(
        candidat_id=job_target.candidat_id,
        job_target_id=job_target.id,
        status="in_progress",
        generated_questions=quiz.model_dump() # Sauvegarde le JSON !
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "questions": quiz
    }

# --- 3. Evaluate Interview Route ---
@app.post("/evaluate-interview")
async def evaluate_interview(request: EvaluateInterviewRequest, db: Session = Depends(get_db)):
    
    # 1. Récupérer la session d'interview
    session = db.query(models.InterviewSession).filter(models.InterviewSession.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session d'interview introuvable")

    # Convertir le JSON sauvegardé en objet Pydantic
    questions_list = QuestionList(**{"questions": session.generated_questions["questions"]})

    # 2. Appeler l'IA pour corriger
    evaluation_result = evaluate_candidate(questions_list, request.candidate_answers)
    
    # 3. Mettre à jour la base de données avec le score et les justifications
    session.status = "completed"
    session.candidate_answers = request.candidate_answers
    session.score_out_of_10 = evaluation_result.score_out_of_10
    session.evaluation_details = [ans.model_dump() for ans in evaluation_result.answer_details]
    
    db.commit()
    
    return evaluation_result