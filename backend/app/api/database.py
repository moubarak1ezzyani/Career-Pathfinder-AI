from app.core.config import db_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# db config
engine=create_engine(db_url)
SessionLocal=sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base=declarative_base()     # ORM models

