from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, JSON
from app.api.database import my_Base
from sqlalchemy.sql import func

# ==========================================
# 1. UTILISATEUR & AUTHENTIFICATION
# ==========================================
class Candidat(my_Base):
    __tablename__ = "candidats"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    hashed_pwd = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

# ==========================================
# 2. GESTION DU CV (Lié à matching_engine.py)
# ==========================================
class Resume(my_Base):     
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    candidat_id = Column(Integer, ForeignKey("candidats.id"))
    
    # Très important pour matching_engine.py (extract_text_from_pdf)
    file_path = Column(String, nullable=False) 
    
    # Pour éviter de repayer Qwen si on a déjà extrait les compétences
    extracted_skills_json = Column(JSON, nullable=True) 
    
    uploaded_at = Column(DateTime, server_default=func.now())

# ==========================================
# 3. L'OFFRE CIBLÉE (Lié à chatbot.py et main.py)
# ==========================================
class JobTarget(my_Base):
    __tablename__ = "job_targets"
    
    id = Column(Integer, primary_key=True, index=True)
    candidat_id = Column(Integer, ForeignKey("candidats.id"))
    
    title = Column(String, index=True)    
    # Le texte brut de l'offre, crucial pour generate_questions et analyze_match
    description_text = Column(String, nullable=False) 
    
    created_at = Column(DateTime, server_default=func.now(), index=True)

# ==========================================
# 4. LE MATCHING (Lié à matching_engine.py -> analyze_match)
# ==========================================
class MatchResults(my_Base):
    __tablename__ = "match_results"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_target_id = Column(Integer, ForeignKey("job_targets.id"))
    
    # Stocke le 'match_score' (ex: 85.5) calculé par util.cos_sim
    overall_score = Column(Float) 
    
    # Stocke le dict 'data' de matching_engine.py 
    # (cv_skills_found, job_skills_required, missing_skills)
    match_details = Column(JSON) 
    
    analyzed_at = Column(DateTime, server_default=func.now(), index=True)

# ==========================================
# 5. L'ENTRETIEN TECHNIQUE (Lié à chatbot.py -> EvaluateInterview)
# ==========================================
class InterviewSession(my_Base):
    __tablename__ = "interview_session"
    
    id = Column(Integer, primary_key=True, index=True)
    candidat_id = Column(Integer, ForeignKey("candidats.id"))
    job_target_id = Column(Integer, ForeignKey("job_targets.id"))
    
    status = Column(String, default="pending") # pending, in_progress, completed
    
    # Stocke le QuestionList généré par Qwen
    generated_questions = Column(JSON, nullable=True) 
    
    # Stocke les réponses brutes tapées par le candidat
    candidate_answers = Column(JSON, nullable=True)
    
    # Stocke le InterviewResult généré par evaluate_candidate
    score_out_of_10 = Column(Integer, nullable=True)
    evaluation_details = Column(JSON, nullable=True) # justify: True/False etc.
    
    started_at = Column(DateTime, server_default=func.now(), index=True)
    ended_at = Column(DateTime, nullable=True)