# we will use sqlalchemy to create a question bank model and store the generated questions in a database.
# we will use postgres for this purpose and we will use sqlalchemy to interact with the database.

from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Integer, String, DateTime, JSON
from app.db.database import Base

class ComprehensionQuestion(Base):
    __tablename__ = "comprehension_questions"
    __table_args__ = (
        CheckConstraint("correct_answer IN ('a','b','c','d')", name="ck_comprehension_correct_answer"),
    )

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    passage = Column(String, nullable=False)
    difficulty = Column(String, index=True)
    question = Column(String, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(String, nullable=True)
    explanation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
