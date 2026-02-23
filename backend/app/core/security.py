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


pwd_context=CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='token')

def verify_pwd(plain_pwd : str, hash_pwd : str) -> bool:
    return pwd_context.verify(plain_pwd, hash_pwd)

def get_pwd_hash(password :str)->str:
    return pwd_context.hash(password)

def create_access_token(data : dict, expire_delta : Optional[time]=None):
    to_encode=data.copy()
    if expire_delta:
        expire= datetime.now(UTC) + expire_delta

    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)

    to_encode.update({"exp" : expire})
    encoded_jwt=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGO)
    return encoded_jwt

def verify_token(token : str ) -> TokenData:
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithm=ALGO )
        email : str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="couldn't verify credentials",
                header={"WWW-AUTH": "Bearer"}
            )
        return token
    
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="couldn't verify credentials",
            header={"WWW-AUTH": "Bearer"}
        )