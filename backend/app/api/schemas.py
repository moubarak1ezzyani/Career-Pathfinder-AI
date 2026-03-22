from pydantic import BaseModel
import datetime
from typing import Optional, List, Dict

# ==========================================
# 1. UTILISATEURS & AUTHENTIFICATION
# ==========================================
class CandidatCreate(BaseModel):
    # L'ID est retiré car il est auto-généré par la base de données
    email: str
    password: str

class CandidatResponse(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        from_attributes = True  # Permet à Pydantic de lire les objets SQLAlchemy

class CandidatLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel): # Renommé avec une majuscule (PEP 8)
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ==========================================
# 2. MATCHING & CV (Anciennement dans matching_engine.py)
# ==========================================
class SkillsExtraction(BaseModel):
    found_skills: List[str]
    required_skills: List[str]

class MatchData(BaseModel):
    cv_skills_found: List[str]
    job_skills_required: List[str]
    missing_skills: List[str]

class MatchResponse(BaseModel):
    status: str
    match_score: float
    data: MatchData

# ==========================================
# 3. CHATBOT & INTERVIEW (Anciennement dans chatbot.py)
# ==========================================
class Question(BaseModel):
    number: int
    question_text: str

class QuestionList(BaseModel):
    questions: List[Question]

class AnswerEvaluation(BaseModel):
    number: int
    is_correct: bool
    justification: str

class InterviewResult(BaseModel):
    score_out_of_10: int
    answer_details: List[AnswerEvaluation]

class EvaluateInterviewRequest(BaseModel):
    session_id: int
    candidate_answers: Dict[int, str]  # ex: {1: "Réponse 1", 2: "Réponse 2"}

# ==========================================
# 4. AUTRES SCHÉMAS (Existant dans ton projet)
# ==========================================
class Offre(BaseModel):
    id: int
    titre: str
    vect_content: str

    class Config:
        from_attributes = True

class SessionCoaching(BaseModel):
    id: int
    date: datetime.datetime
    score: float
    type_entrainement: str

    class Config:
        from_attributes = True

class ResultatVideo(BaseModel):
    id: int
    emotion_dominante: str
    timestamp: float

    class Config:
        from_attributes = True