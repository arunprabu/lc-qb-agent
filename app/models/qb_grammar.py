# we will use sqlalchemy to create a question bank model and store the generated questions in a database.
# we will use postgres for this purpose and we will use sqlalchemy to interact with the database.
# we will create a question bank model with the following fields:
# id: int (primary key)
# topic: str
# difficulty: str (beginner, intermediate, advanced)
# question: str
# options: list (only for grammar questions)
# correct_answer: str (only for grammar questions)
# explanation: str (only for grammar questions)
# created_at: datetime
# updated_at: datetime

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GrammarQuestion(Base):
    __tablename__ = "grammar_questions"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    difficulty = Column(String, index=True)
    question = Column(String, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(String, nullable=True)
    explanation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

