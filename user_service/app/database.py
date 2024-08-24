from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional

DB_URL = "postgresql://ziakhan:my_password@PostgresUserCont:5432/user_service_db"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

# Import all your models here
from app.models import User  # Replace with the actual path to your models

# Create the database tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
