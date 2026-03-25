from app.core.config import DB_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# db config
engine=create_engine(DB_URL)
SessionLocal=sessionmaker(bind=engine, autocommit=False, autoflush=False)
my_Base=declarative_base()     # ORM models

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
