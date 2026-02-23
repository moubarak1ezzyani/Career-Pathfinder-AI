from pydantic import BaseModel
import datetime
from typing import Optional

class CandidatCreate(BaseModel):
    id : int
    email : str
    password : str
    # hash_cv : str

class CandidatResponse(BaseModel):
    id : int
    email : str
    is_active : bool

class CandidatLogin(BaseModel):
    email : str
    password : str

class token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    email : Optional[str] =  None


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
 
