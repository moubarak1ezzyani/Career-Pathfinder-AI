from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ==========================================
# 1. USERS & AUTHENTICATION
# ==========================================
class CandidatCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None  # Added to match models.py

class CandidatResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy objects

class CandidatLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ==========================================
# 2. MATCHING ENGINE & CV
# ==========================================
# Used by Qwen for extraction
class SkillsExtraction(BaseModel):
    found_skills: list[str]
    required_skills: list[str]

# Used for the final API response
class MatchData(BaseModel):
    cv_skills_found: list[str]
    job_skills_required: list[str]
    missing_skills: list[str]

class MatchResponse(BaseModel):
    status: str
    match_score: float
    data: MatchData

# ==========================================
# 3. CHATBOT & INTERVIEW 
# ==========================================
# Used by Qwen to generate the quiz
class Question(BaseModel):
    number: int
    question_text: str

class QuestionList(BaseModel):
    questions: list[Question]

# Used by Qwen to grade the answers
class AnswerEvaluation(BaseModel):
    number: int
    is_correct: bool
    justification: str

class InterviewResult(BaseModel):
    score_out_of_10: int
    answer_details: list[AnswerEvaluation]

# Used by the API endpoint to receive user answers
class EvaluateInterviewRequest(BaseModel):
    session_id: int
    candidate_answers: dict[int, str]  # e.g., {1: "Answer 1", 2: "Answer 2"}

# ==========================================
# 4. DATABASE ENTITY RESPONSES (Mapped to models.py)
# ==========================================
class ResumeResponse(BaseModel):
    id: int
    candidat_id: int
    file_path: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class JobTargetResponse(BaseModel):
    id: int
    candidat_id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class InterviewSessionResponse(BaseModel):
    id: int
    candidat_id: int
    job_target_id: int
    status: str
    score_out_of_10: Optional[int]
    started_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# 5. LEGACY / OTHER SCHEMAS 
# ==========================================
class Offre(BaseModel):
    id: int
    titre: str
    vect_content: str

    class Config:
        from_attributes = True

class SessionCoaching(BaseModel):
    id: int
    date: datetime
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