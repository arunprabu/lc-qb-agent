# Question Bank Agent — Architecture

## Overview

An AI-powered REST API that generates assessment questions (grammar MCQs and reading comprehension) on demand. A LangChain agent orchestrates three specialist LLM-powered tools, produces structured output, and persists the results to a PostgreSQL database.

---

## Request Flow

```
Client (HTTP POST /api/v1/generate-qb)
        │
        ▼
┌───────────────────┐
│   FastAPI Router  │  qb_routes.py
│                   │  validates: type, topic, difficulty, count
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  QuestionBank     │  qb_service.py
│  Service          │  calls run_agent(), then saves to DB
└────────┬──────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│              QB Agent  (qb_agent.py)          │
│                                              │
│  LangChain create_agent                      │
│  model: gpt-4o-mini                          │
│  response_format: QuestionBankOutput         │
│  system_prompt: SYSTEM_PROMPT                │
│                                              │
│  ReAct loop                                  │
│  ┌─────────────────────────────────────┐    │
│  │  Reason → pick tool → observe       │    │
│  │  repeat until final answer          │    │
│  └─────────────────────────────────────┘    │
│                                              │
│  Tools available to agent:                  │
│  ┌──────────────────────────────────────┐   │
│  │ 1. generate_grammar_mcqs             │   │
│  │    gpt-4o-mini + with_structured_    │   │
│  │    output(GrammarMCQListOutput)      │   │
│  ├──────────────────────────────────────┤   │
│  │ 2. generate_comprehension_passages   │   │
│  │    gpt-4o-mini + with_structured_    │   │
│  │    output(ComprehensionPassage)      │   │
│  ├──────────────────────────────────────┤   │
│  │ 3. validate_question_quality         │   │
│  │    gpt-4o-mini + with_structured_    │   │
│  │    output(ValidationResult)          │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  structured_response → QuestionBankOutput   │
│  inject topic + difficulty per question     │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌───────────────────┐
│   DB Repository   │  app/db/repository.py
│                   │  save_grammar_questions()
│                   │  save_comprehension_questions()
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   PostgreSQL      │
│                   │
│  grammar_         │
│  questions        │
│                   │
│  comprehension_   │
│  questions        │
└───────────────────┘
```

---

## Agent Tool Routing Logic

The agent's `SYSTEM_PROMPT` defines strict routing rules:

| User request type                              | Tool called                       | LLM call inside tool                   |
| ---------------------------------------------- | --------------------------------- | -------------------------------------- |
| Grammar (tenses, voice, parts of speech, etc.) | `generate_grammar_mcqs`           | `gpt-4o-mini` → `GrammarMCQListOutput` |
| Comprehension / reading passages               | `generate_comprehension_passages` | `gpt-4o-mini` → `ComprehensionPassage` |
| After generation (always)                      | `validate_question_quality`       | `gpt-4o-mini` → `ValidationResult`     |

The agent never generates grammar or comprehension questions itself — it delegates entirely to the tools and returns their output unchanged.

---

## Structured Output Chain

```
Agent final response
        │
        │  response_format=QuestionBankOutput
        ▼
QuestionBankOutput
  └── questions: List[QuestionOutput]
        ├── question: str
        ├── options: Optional[List[str]]
        ├── correct_answer: Optional[str]
        ├── explanation: Optional[str]
        └── passage: Optional[str]
        (topic + difficulty injected from run_agent params)
        │
        ▼
  list of plain dicts  →  DB insert
```

---

## Data Models

### Grammar Question (PostgreSQL table: `grammar_questions`)

| Column         | Type       | Notes                              |
| -------------- | ---------- | ---------------------------------- |
| id             | Integer PK | auto-increment                     |
| topic          | String     | indexed                            |
| difficulty     | String     | beginner / intermediate / advanced |
| question       | String     | the MCQ question text              |
| options        | JSON       | list of 4 options                  |
| correct_answer | String     | e.g. "A. The cake was eaten..."    |
| explanation    | String     | brief explanation                  |
| created_at     | DateTime   | UTC timestamp                      |

### Comprehension Question (PostgreSQL table: `comprehension_questions`)

| Column         | Type       | Notes                              |
| -------------- | ---------- | ---------------------------------- |
| id             | Integer PK | auto-increment                     |
| topic          | String     | indexed                            |
| difficulty     | String     | beginner / intermediate / advanced |
| passage        | Text       | the reading passage                |
| question       | String     | the question about the passage     |
| options        | JSON       | list of 4 options                  |
| correct_answer | String     |                                    |
| explanation    | String     |                                    |
| created_at     | DateTime   | UTC timestamp                      |

---

## Folder Structure

```
question-bank-agent/
├── app/
│   ├── main.py                  FastAPI app, router registration
│   ├── agent/
│   │   ├── qb_agent.py          build_agent(), run_agent(), Pydantic output models
│   │   └── prompts.py           SYSTEM_PROMPT + all tool prompt templates
│   ├── tools/
│   │   ├── grammar_tool.py      generate_grammar_mcqs()
│   │   ├── comprehension_tool.py  generate_comprehension_passages()
│   │   └── validate_question_quality_tool.py  validate_question_quality()
│   ├── models/                  SQLAlchemy ORM table definitions
│   │   ├── qb_grammar.py        GrammarQuestion
│   │   └── qb_comprehension.py  ComprehensionQuestion
│   ├── db/
│   │   ├── database.py          engine, SessionLocal, get_db
│   │   └── repository.py        save_grammar_questions(), save_comprehension_questions()
│   ├── services/
│   │   └── qb_service.py        QuestionBankService.execute_agent()
│   └── routes/
│       └── qb_routes.py         POST /generate-qb, GET /health
├── reference/
│   ├── architecture.md          this file
│   ├── db-implementation.md     step-by-step DB setup guide
│   ├── agenda.md
│   ├── notes.md
│   └── todos.md
├── .env                         secrets (not committed)
├── .env.example                 template
└── pyproject.toml               dependencies
```

---

## API

### `POST /api/v1/generate-qb`

**Request body:**

```json
{
  "type": "grammar",
  "topic": "passive voice",
  "difficulty": "intermediate",
  "count": "3"
}
```

**Response:**

```json
{
  "message": "Agent execution complete at service level",
  "type": "grammar",
  "topic": "passive voice",
  "difficulty": "intermediate",
  "count": "3",
  "questions": [
    {
      "question": "Select the sentence that correctly uses the passive voice.",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "A. The cake was eaten by the children.",
      "explanation": "In the passive voice, the focus is on the action being done to the subject.",
      "topic": "passive voice",
      "difficulty": "intermediate"
    }
  ]
}
```

### `GET /api/v1/health`

```json
{ "status": "ok" }
```

---

## Tech Stack

| Layer             | Technology                                                 |
| ----------------- | ---------------------------------------------------------- |
| API framework     | FastAPI                                                    |
| Agent framework   | LangChain 1.x (`create_agent`)                             |
| LLM               | OpenAI `gpt-4o-mini`                                       |
| Structured output | Pydantic v2 + `with_structured_output` / `response_format` |
| Database          | PostgreSQL                                                 |
| ORM               | SQLAlchemy 2.x                                             |
| Migrations        | Alembic                                                    |
| Runtime           | Python 3.11, uvicorn                                       |
| Package manager   | uv                                                         |
