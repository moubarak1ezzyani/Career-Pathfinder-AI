import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt

# --- Importation de tes propres modules ---
from api.database import get_db, engine
import models
import schemas
from config import SECRET_KEY, ALGO
from security import get_pwd_hash, verify_pwd, create_access_token, oauth2_scheme

# Importation de tes moteurs d'IA
from matching_engine import analyze_match
from chatbot import generate_questions, evaluate_candidate

# Création des tables dans la base de données
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
# DEPENDANCES (Le fameux "verrou" de sécurité)
# ==========================================
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Vérifie le token et retourne l'utilisateur actuellement connecté."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide ou expiré")
    
    user = db.query(models.Candidat).filter(models.Candidat.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur non trouvé")
    
    return user


# ==========================================
# ROUTES PUBLIQUES : AUTHENTIFICATION
# ==========================================
@app.post("/register", response_model=schemas.CandidatResponse)
def register(user: schemas.CandidatCreate, db: Session = Depends(get_db)):
    # Vérifier si l'email existe déjà
    db_user = db.query(models.Candidat).filter(models.Candidat.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    
    # Création du compte
    hashed_pwd = get_pwd_hash(user.password)
    # On prend la première partie de l'email comme nom par défaut
    nom_par_defaut = user.email.split("@")[0] 
    
    new_user = models.Candidat(email=user.email, hashed_pwd=hashed_pwd, name=nom_par_defaut)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Candidat).filter(models.Candidat.email == form_data.username).first()
    
    if not user or not verify_pwd(form_data.password, user.hashed_pwd):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# ==========================================
# ROUTES PRIVÉES : MOTEURS D'IA
# ==========================================

# --- 1. CV Analysis Route ---
@app.post("/analyze")
async def analyze_cv(
    file: UploadFile = File(...), 
    job_description: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.Candidat = Depends(get_current_user) # <-- Route protégée !
):
    # 1. Sauvegarder physiquement le fichier PDF
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Lier le CV et l'offre au VRAI candidat connecté
    resume = models.Resume(candidat_id=current_user.id, file_path=file_location)
    job_target = models.JobTarget(candidat_id=current_user.id, description_text=job_description)
    db.add(resume)
    db.add(job_target)
    db.commit()
    db.refresh(resume)
    db.refresh(job_target)

    # 3. Appeler le moteur d'IA
    result = analyze_match(cv_file_path=file_location, job_description=job_description)

    if result["status"] == "success":
        # 4. Sauvegarder les résultats
        match_result = models.MatchResults(
            resume_id=resume.id,
            job_target_id=job_target.id,
            overall_score=result["match_score"],
            match_details=result["data"]
        )
        db.add(match_result)
        db.commit()

    return {
        "candidat_id": current_user.id,
        "job_target_id": job_target.id,
        "ai_result": result
    }

# --- 2. Generate Interview Questions Route ---
@app.post("/generate-quiz")
async def generate_quiz(
    job_target_id: int = Form(...), 
    db: Session = Depends(get_db),
    current_user: models.Candidat = Depends(get_current_user) # <-- Route protégée !
):
    # Sécurité : vérifier que l'offre appartient bien au candidat connecté
    job_target = db.query(models.JobTarget).filter(
        models.JobTarget.id == job_target_id, 
        models.JobTarget.candidat_id == current_user.id
    ).first()
    
    if not job_target:
        raise HTTPException(status_code=404, detail="Offre introuvable ou accès refusé")

    quiz = generate_questions(job_target.description_text)
    
    session = models.InterviewSession(
        candidat_id=current_user.id,
        job_target_id=job_target.id,
        status="in_progress",
        generated_questions=quiz.model_dump()
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
async def evaluate_interview(
    request: schemas.EvaluateInterviewRequest, 
    db: Session = Depends(get_db),
    current_user: models.Candidat = Depends(get_current_user) # <-- Route protégée !
):
    # Sécurité : vérifier que la session appartient au candidat
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == request.session_id,
        models.InterviewSession.candidat_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable ou accès refusé")

    # On recrée l'objet Pydantic depuis la base de données
    questions_list = schemas.QuestionList(**{"questions": session.generated_questions["questions"]})

    # Correction par l'IA
    evaluation_result = evaluate_candidate(questions_list, request.candidate_answers)
    
    # Mise à jour DB
    session.status = "completed"
    session.candidate_answers = request.candidate_answers
    session.score_out_of_10 = evaluation_result.score_out_of_10
    session.evaluation_details = [ans.model_dump() for ans in evaluation_result.answer_details]
    
    db.commit()
    
    return evaluation_result