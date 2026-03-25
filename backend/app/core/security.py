from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from app.core.config import SECRET_KEY, ALGO

# Password hashing and authentication scheme configuration
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

# "login" is the URL where FastAPI will fetch the token in Swagger (instead of 'token')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login') 

def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_pwd(plain_pwd: str, hash_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hash_pwd)

def create_access_token(data: dict):
    to_encode = data.copy()
   
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGO)
    return encoded_jwt