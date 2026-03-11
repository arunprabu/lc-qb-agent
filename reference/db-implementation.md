# DB Implementation Guide

## Should we rename `models/` to `schemas/`?

**No. Keep `models/`.** Here's the reasoning:

- In SQLAlchemy, the ORM classes that map to database tables are called **models** — this is the standard convention used in FastAPI + SQLAlchemy projects.
- `schemas/` is the FastAPI convention for **Pydantic schemas** (request/response shapes). We already have Pydantic models living inside the agent (`QuestionOutput`, `QuestionBankOutput`) and tools (`GrammarMCQ`, etc.).
- If you introduce both, the standard layout is:
  - `app/models/` — SQLAlchemy ORM table definitions ← **keep this**
  - `app/schemas/` — Pydantic request/response models ← **create this later if needed**

---

## Step 1 — Add dependencies

Add to `pyproject.toml` under `dependencies`:

```toml
"sqlalchemy>=2.0",
"psycopg2-binary>=2.9",
"alembic>=1.13",
```

Then run:

```bash
uv sync
```

---

## Step 2 — Add DB config to `.env.example`

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/question_bank_db
```

Copy to your `.env` and fill in your actual Postgres credentials.

---

## Step 3 — Create `app/db/database.py`

This is the SQLAlchemy engine + session setup.

```python
# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Step 4 — Finish `app/models/qb_comprehension.py`

`qb_grammar.py` is already done. Add the SQLAlchemy model to `qb_comprehension.py`:

```python
# app/models/qb_comprehension.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ComprehensionQuestion(Base):
    __tablename__ = "comprehension_questions"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    difficulty = Column(String, index=True)
    passage = Column(Text, nullable=False)
    question = Column(String, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(String, nullable=True)
    explanation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## Step 5 — Create `app/db/repository.py`

This handles the actual INSERT logic, called from the service layer.

```python
# app/db/repository.py
from sqlalchemy.orm import Session
from app.models.qb_grammar import GrammarQuestion
from app.models.qb_comprehension import ComprehensionQuestion

def save_grammar_questions(db: Session, questions: list[dict]):
    for q in questions:
        record = GrammarQuestion(
            topic=q["topic"],
            difficulty=q["difficulty"],
            question=q["question"],
            options=q.get("options"),
            correct_answer=q.get("correct_answer"),
            explanation=q.get("explanation"),
        )
        db.add(record)
    db.commit()

def save_comprehension_questions(db: Session, questions: list[dict]):
    for q in questions:
        record = ComprehensionQuestion(
            topic=q["topic"],
            difficulty=q["difficulty"],
            passage=q.get("passage"),
            question=q["question"],
            options=q.get("options"),
            correct_answer=q.get("correct_answer"),
            explanation=q.get("explanation"),
        )
        db.add(record)
    db.commit()
```

---

## Step 6 — Update `app/services/qb_service.py`

Wire the repository into the service layer:

```python
# app/services/qb_service.py
from app.agent.qb_agent import run_agent
from app.db.repository import save_grammar_questions, save_comprehension_questions
from app.db.database import SessionLocal

class QuestionBankService:

    async def execute_agent(self, type: str, topic: str, difficulty: str, count: str):
        print(f"SERVICE: Executing agent for topic: {topic} with difficulty: {difficulty} and count: {count} and type: {type}")

        result = await run_agent(type, topic, difficulty, count)
        questions = result["questions"]

        db = SessionLocal()
        try:
            if type == "grammar":
                save_grammar_questions(db, questions)
            elif type == "comprehension":
                save_comprehension_questions(db, questions)
        finally:
            db.close()

        return {
            "message": "Agent execution complete at service level",
            "questions": questions,
            "type": type,
            "topic": topic,
            "difficulty": difficulty,
            "count": count,
        }
```

---

## Step 7 — Create tables with Alembic

### One-time setup

```bash
alembic init alembic
```

Edit `alembic/env.py` — replace the `target_metadata` line:

```python
from app.models.qb_grammar import Base as GrammarBase
from app.models.qb_comprehension import Base as ComprehensionBase

# combine both metadata objects
from sqlalchemy import MetaData
target_metadata = [GrammarBase.metadata, ComprehensionBase.metadata]
```

Also set the DB URL in `alembic.ini`:

```ini
sqlalchemy.url = postgresql://postgres:password@localhost:5432/question_bank_db
```

Or better, read it from the env in `alembic/env.py`:

```python
import os
from dotenv import load_dotenv
load_dotenv()
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
```

### Generate and run the first migration

```bash
alembic revision --autogenerate -m "create grammar and comprehension tables"
alembic upgrade head
```

---

## Step 8 — Create the Postgres database (if not done yet)

```bash
psql -U postgres -c "CREATE DATABASE question_bank_db;"
```

---

## Final folder structure after all steps

```
app/
  db/
    database.py       ← engine + SessionLocal + get_db
    repository.py     ← save_grammar_questions, save_comprehension_questions
  models/
    qb_grammar.py     ← GrammarQuestion ORM model  (done)
    qb_comprehension.py ← ComprehensionQuestion ORM model  (step 4)
  services/
    qb_service.py     ← updated to call repository  (step 6)
alembic/              ← migration files  (step 7)
alembic.ini
```
