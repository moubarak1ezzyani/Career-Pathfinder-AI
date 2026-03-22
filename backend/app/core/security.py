from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from config import SECRET_KEY, ALGO

# Configuration du hash et du schéma d'authentification
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
# "login" est l'URL où FastAPI ira chercher le token dans Swagger (au lieu de 'token')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login') 

def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_pwd(plain_pwd: str, hash_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hash_pwd)

def create_access_token(data: dict):
    to_encode = data.copy()
    # Expiration simple codée en dur (ou tu peux utiliser TOKEN_EXPIRE de ton config.py)
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGO)
    return encoded_jwt