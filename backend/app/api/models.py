from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Datetime, JSON
from api.database import Base
import datetime
from sqlalchemy.sql import func

class Candidat(Base):
    __tablename__="candidats"
    id=Column(Integer, primary_key=True, index=True)
    email=Column(String, unique=True, index=True)
    name=Column(String, index=True)
    created_at=Column(DateTime, server_default=func.now(), index=True)
    # hash_cv=Column(String)      # Stores the reference/hash of the CV file

class Resume(Base):     # uploaded cv 
    __tablename__="resumes"
    id=Column(Integer, primary_key=True, index=True)
    candidat_id=Column(Integer, ForeignKey("candidats.id"))
    file_path=Column(String)
    raw_text=Column(String)
    uploaded_at=Column(DateTime)

class JobTarget(Base):
    __tablename__="job_targets"
    id=Column(Integer, primary_key=True, index=True)
    candidat_id=Column(Integer, ForeignKey("candidats.id"))
    title=Column(String, index=True)    # Ex: "dev python Junior"
    description_text=Column(String)     # text collé par l utilisateur
    created_at=Column(Datetime, server_default=func.now(), index=True)

class MatchResults(Base):
    __tablename__="match_results"
    id=Column(Integer, primary_key=True, index=True)
    resume_id=Column(Integer, ForeignKey("resumes.id"))
    job_target_id=Column(Integer, ForeignKey("job_targets.id"))
    overall_score=Column(Float)
    missing_skills=Column(JSON)
    analyzed_at=Column(Datetime, server_default=func.now(), index=True)

class CoverLetters(Base):
    __tablename__="cover_letters"
    id=Column(Integer, primary_key=True, index=True)
    resume_id=Column(Integer, ForeignKey("resumes.id"))
    job_target_id=Column(Integer, ForeignKey("job_targets.id"))
    generated_content=Column(String)
    created_at=Column(Datetime, server_default=func.now(), index=True)

class InterviewSession(Base):
    __tablename__="interview_session"
    id=Column(Integer, primary_key=True, index=True)
    candidat_id=Column(Integer, ForeignKey("candidats.id"))
    job_target_id=Column(Integer, ForeignKey("job_targets.id"))
    status=Column(String)
    started_at=Column(Datetime, server_default=func.now(), index=True)
    ended_at=Column(Datetime, server_default=func.now(), index=True)

class InterviewMessage(Base):   # Historique du Chatbot
    __tablename__="interview_message"
    id=Column(Integer, primary_key=True, index=True)
    session_id=Column(Integer, ForeignKey("interview_session.id"))
    sender=Column(String)
    content=Column(String)
    created_at=Column(Datetime, server_default=func.now(), index=True)

class SoftSkillsEvaluation(Base):
    __tablename__="soft_skills_evaluation"
    id=Column(Integer, primary_key=True, index=True)
    session_id=Column(Integer, ForeignKey("interview_session.id"))
    stress_score=Column(Float)
    confidence_score=Column(Float)
    communication_score=Column(Float)
    emotional_timeline=Column(JSON)

# class Offre(Base):
#     __tablename__="offres"
#     id=Column(Integer, primary_key=True, index=True)
#     titre=Column(String, index=True)
#     # Using String or Text for vector data (or PickledType/JSON depending on your vector DB)
#     vect_content=Column(String)

# class SessionCoaching(Base):
#     __tablename__="session_coaching"
#     id=Column(Integer, primary_key=True, index=True)
#     date=Column(DateTime, default=datetime.datetime.utc())
#     score_matching=Column(Float)
#     type_entrainement=Column(String)      # e.g., "Interview", "Technical"

# class ResultatVideo(Base):
#     __tablename__="resultat_video"
#     id=Column(Integer, primary_key=True, index=True)
#     emotion_dominante=Column(String)
#     timestamp=Column(Float)

    





