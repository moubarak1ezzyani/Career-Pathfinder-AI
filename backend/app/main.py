# files imports
from api.database import my_Base, engine
from api.schemas import password, TokenData
from core.config import SECRET_KEY, ALGO, TOKEN_EXPIRE

# Libs
from fastapi import FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
import jwt
from typing import Optional
from datetime import time, timedelta, datetime, UTC, minutes


    



# ------------------------------------
my_Base.metada.create_all(bind=engine)
my_app = FastAPI()

# check app
@my_app.get("/")
def read_root():
    return {"message":"Hello World"}


@my_app.post("/Register")
def sign_up():
    pass