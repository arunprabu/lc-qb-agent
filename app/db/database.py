# app/db/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# loading environment variables from .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# creating the database engine 
engine = create_engine(DATABASE_URL)

# creating session factory for database interactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# shared declarative base for all ORM models
Base = declarative_base()

# dependency for fast api
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# let's test the database connection by running this file directly
if __name__ == "__main__":
    print("Testing database connection...")

    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        print("Database connection successful.")
    except Exception as e:
        print("Database connection failed")
    finally:
        db.close()

# to create db 
# psql -U <username> -c "CREATE DATABASE question_bank_db;"