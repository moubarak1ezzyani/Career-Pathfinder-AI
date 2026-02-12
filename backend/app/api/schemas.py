from pydantic import BaseModel
import datetime

class Candidat(BaseModel):
    id : int
    email : str
    hash_cv : str

class Offre(BaseModel):
    id : int
    titre : str
    vect_content : str

class SessionCoaching(BaseModel):
    id : int
    date : datetime.datetime
    score : float
    type_entrainement : str

class ResultatVideo(BaseModel):
    id : int
    emotion_dominante : str
    timestamp : float
 
