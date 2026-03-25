import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt

# --- Import custom modules ---
from app.api.database import get_db, engine
from app.api import models
from app.api import schemas
from app.core.config import SECRET_KEY, ALGO
from app.core.security import get_pwd_hash, verify_pwd, create_access_token, oauth2_scheme

# Import AI engines
from app.services.matching_engine import analyze_match
from app.chatbot import generate_questions, evaluate_candidate
# NEW: Import the video analysis service
from app.services.video_analyzer import analyze_video_offline

# Create database tables
models.my_Base.metadata.create_all(bind=engine)

app = FastAPI(title="Career Pathfinder AI", version="1.0")

# --- CORS CONFIG ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001", 
        "http://127.0.0.1:3001"  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local directories for uploads
UPLOAD_DIR = "uploads/cvs"
VIDEO_DIR = "uploads/videos" # Directory for video files
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


# ==========================================
# DEPENDENCIES (The security "lock")
# ==========================================
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Verifies the token and returns the currently authenticated user."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    user = db.query(models.Candidat).filter(models.Candidat.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user


# ==========================================
# PUBLIC ROUTES: AUTHENTICATION
# ==========================================
@app.post("/register", response_model=schemas.CandidatResponse)
def register(user: schemas.CandidatCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    db_user = db.query(models.Candidat).filter(models.Candidat.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="This email is already in use")
    
    # Create account
    hashed_pwd = get_pwd_hash(user.password)
    # Use first part of email as default name
    default_name = user.email.split("@")[0] 
    new_user = models.Candidat(email=user.email, hashed_pwd=hashed_pwd, name=default_name)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Candidat).filter(models.Candidat.email == form_data.username).first()
    if not user or not verify_pwd(form_data.password, user.hashed_pwd):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# ==========================================
# PRIVATE ROUTES: AI ENGINES
# ==========================================

# --- 1. CV Analysis Route ---
@app.post("/analyze")
async def analyze_cv(
    file: UploadFile = File(...), 
    job_description: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.Candidat = Depends(get_current_user)
):
    # Save the PDF file physically
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Link CV and job target to the authenticated candidate
    resume = models.Resume(candidat_id=current_user.id, file_path=file_location)
    job_target = models.JobTarget(candidat_id=current_user.id, description_text=job_description)
    db.add(resume)
    db.add(job_target)
    db.commit()
    db.refresh(resume)
    db.refresh(job_target)

    # Call AI engine
    result = analyze_match(cv_file_path=file_location, job_description=job_description)

    if result["status"] == "success":
        # Save results to DB
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
    current_user: models.Candidat = Depends(get_current_user)
):
    # Security: verify job offer belongs to authenticated candidate
    job_target = db.query(models.JobTarget).filter(
        models.JobTarget.id == job_target_id, 
        models.JobTarget.candidat_id == current_user.id
    ).first()
    
    if not job_target:
        raise HTTPException(status_code=404, detail="Job offer not found or access denied")

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
    current_user: models.Candidat = Depends(get_current_user)
):
    # Security: verify session belongs to candidate
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == request.session_id,
        models.InterviewSession.candidat_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or access denied")

    questions_list = schemas.QuestionList(**{"questions": session.generated_questions["questions"]})
    evaluation_result = evaluate_candidate(questions_list, request.candidate_answers)
    
    # Update DB
    session.status = "completed"
    session.candidate_answers = request.candidate_answers
    session.score_out_of_10 = evaluation_result.score_out_of_10
    session.evaluation_details = [ans.model_dump() for ans in evaluation_result.answer_details]
    db.commit()
    
    return evaluation_result


# --- 4. NEW: Video Analysis Route (Route 3) ---
@app.post("/analyze-video")
async def analyze_video(
    file: UploadFile = File(...),
    current_user: models.Candidat = Depends(get_current_user)
):
    # 1. Temporary video storage
    video_path = f"{VIDEO_DIR}/{file.filename}"
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Call the analysis service
        analysis_result = analyze_video_offline(video_path)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])

        # 3. Return the requested results
        return {
            "status": "success",
            "candidate": current_user.name,
            "vision_metrics": analysis_result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")
    
    finally:
        # 4. Cleanup: remove video after processing
        if os.path.exists(video_path):
            os.remove(video_path)