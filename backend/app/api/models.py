from sqlalchemy import Column, Integer, String, DateTime, Float
from api.database import Base
import datetime

class Candidat(Base):
    __tablename__="candidats"
    id=Column(Integer, primary_key=True, index=True)
    email=Column(String, unique=True, index=True)
    hash_cv=Column(String)      # Stores the reference/hash of the CV file

class Offre(Base):
    __tablename__="offres"
    id=Column(Integer, primary_key=True, index=True)
    titre=Column(String, index=True)
    # Using String or Text for vector data (or PickledType/JSON depending on your vector DB)
    vect_content=Column(String)

class SessionCoaching(Base):
    __tablename__="session_coaching"
    id=Column(Integer, primary_key=True, index=True)
    date=Column(DateTime, default=datetime.datetime.utc())
    score_matching=Column(Float)
    type_entrainement=Column(String)      # e.g., "Interview", "Technical"

class ResultatVideo(Base):
    __tablename__="resultat_video"
    id=Column(Integer, primary_key=True, index=True)
    emotion_dominante=Column(String)
    timestamp=Column(Float)

    





