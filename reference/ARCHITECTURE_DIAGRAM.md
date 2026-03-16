# Evaluation Agent Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT REQUESTS                          │
│ (REST API calls to evaluation endpoints)                        │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API ROUTES                                  │
│                 (evaluation_routes.py)                           │
├─────────────────────────────────────────────────────────────────┤
│ POST /agentic-evaluation/grammar      ──► Grammar Evaluation    │
│ POST /agentic-evaluation/reading      ──► Reading Evaluation    │
│ POST /agentic-evaluation/listening    ──► Listening Evaluation  │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EVALUATION SERVICE                             │
│              (evaluation_service.py)                             │
│                                                                  │
│  execute_evaluation(type, **kwargs)                             │
│         │                                                        │
│         └─────► Calls evaluation agent                          │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│               EVALUATION AGENT                                   │
│            (evaluation_agent.py)                                 │
│                                                                  │
│  build_evaluation_agent() ──► Creates LangChain Agent           │
│  run_evaluation_agent(type)  ─► Executes evaluation             │
│                                                                  │
│  Contains:                                                       │
│  ├─ Middleware: ToolCallLimitMiddleware (max 1 call per req)   │
│  ├─ Model: gpt-4o-mini                                          │
│  └─ System Prompt: EVALUATION_SYSTEM_PROMPT                     │
└──────────────────┬──────────────────────────────────────────────┘
                   │
         ┌─────────┴──────────┬─────────────────┐
         │                    │                 │
         ▼                    ▼                 ▼
┌────────────────┐    ┌────────────────┐    ┌─────────────────┐
│   GRAMMAR      │    │    READING     │    │    LISTENING    │
│ EVALUATION     │    │   EVALUATION   │    │   EVALUATION    │
│    TOOL        │    │     TOOL       │    │     TOOL        │
├────────────────┤    ├────────────────┤    ├─────────────────┤
│ Input:         │    │ Input:         │    │ Input:          │
│ - passage      │    │ - passage      │    │ - passage       │
│ - transcript   │    │ - transcript   │    │ - questions     │
│                │    │ - duration(s)  │    │ - answers       │
│ Process:       │    │ - min/max WPM  │    │                 │
│ - Compare text │    │                │    │ Process:        │
│ - LLM analysis │    │ Process:       │    │ - Score answers │
│                │    │ - Calculate WPM│    │ - LLM analysis  │
│ Output:        │    │ - Assess fluency   │- Comprehension  │
│ - Accuracy     │    │ - Pronunciation    │ - Key points    │
│ - Errors       │    │                    │ - Feedback      │
│ - Feedback     │    │ Output:            │                 │
│                │    │ - WPM score        │ Output:         │
│                │    │ - WPM assessment   │ - Comprehension │
│                │    │ - Fluency score    │ - Accuracy %    │
│                │    │ - Pronunciation    │ - Understanding │
│                │    │ - Overall score    │ - Suggestions   │
│                │    │ - Feedback         │                 │
└────────┬───────┘    └────────┬────────┘    └────────┬────────┘
         │                     │                     │
         └─────────────────────┴─────────────────────┘
                        │
                        ▼
              ┌──────────────────────┐
              │   LLM (OpenAI)       │
              │    gpt-4o-mini       │
              │  temperature: 0.3    │
              │  max_tokens: 1500    │
              │  structured output   │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Structured Result   │
              │   (JSON/Pydantic)    │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   FORMAT RESPONSE    │
              │  and Return to Client│
              └──────────────────────┘
```

---

## Component Interaction Flow

### Grammar Evaluation Flow

```
Client Request
    │
    ├─ POST /api/v1/candidates/agentic-evaluation
    │
    ▼
GrammarEvaluationRequest
    │
    ├─ original_passage: str
    ├─ transcribed_text: str
    │
    ▼
agentic_evaluation_with_grammar()
    │
    ▼
evaluation_service.execute_evaluation("grammar", ...)
    │
    ▼
evaluation_agent.run_evaluation_agent("grammar", **kwargs)
    │
    ├─ build_evaluation_agent()
    ├─ agent.invoke(messages)
    │
    ▼
Agent selects evaluate_grammar tool
    │
    ▼
grammar_evaluation_tool.evaluate_grammar(passage, transcript)
    │
    ├─ Calculate similarity
    ├─ Call LLM for analysis
    │
    ▼
Structured GrammarEvaluationOutput
    │
    ├─ accuracy_score: 85.5
    ├─ error_count: 2
    ├─ error_types: [...]
    ├─ feedback: str
    ├─ overall_assessment: str
    │
    ▼
Format and Return Response
```

---

## Reading Evaluation Flow

```
Client Request
    │
    ├─ POST /api/v1/candidates/agentic-evaluation/reading
    │
    ▼
ReadingEvaluationRequest
    │
    ├─ original_passage: str
    ├─ transcribed_text: str
    ├─ audio_duration_seconds: float
    ├─ min_wpm: int (default 140)
    ├─ max_wpm: int (default 170)
    │
    ▼
agentic_evaluation_reading()
    │
    ▼
evaluation_service.execute_evaluation("reading", ...)
    │
    ▼
evaluation_agent.run_evaluation_agent("reading", **kwargs)
    │
    ▼
Agent selects evaluate_reading tool
    │
    ▼
reading_evaluation_tool.evaluate_reading(passage, transcript, duration)
    │
    ├─ Calculate WPM = words / (duration / 60)
    ├─ Classify speed (below/avg/above/excellent)
    ├─ Call LLM for fluency analysis
    │
    ▼
Structured ReadingEvaluationOutput
    │
    ├─ reading_speed_wpm: 155.5
    ├─ reading_speed_assessment: "average"
    ├─ fluency_score: 78.0
    ├─ pronunciation_accuracy: 82.5
    ├─ overall_score: 80.2
    ├─ feedback: str
    ├─ recommendations: str
    │
    ▼
Format and Return Response
```

---

## Listening Evaluation Flow

```
Client Request
    │
    ├─ POST /api/v1/candidates/agentic-evaluation/listening
    │
    ▼
ListeningEvaluationRequest
    │
    ├─ passage: str
    ├─ questions_and_answers: List[QuestionAnswerPair]
    │   ├─ question: str
    │   ├─ candidate_answer: str
    │   ├─ correct_answer: str
    │
    ▼
agentic_evaluation_listening()
    │
    ▼
evaluation_service.execute_evaluation("listening", ...)
    │
    ▼
evaluation_agent.run_evaluation_agent("listening", **kwargs)
    │
    ▼
Agent selects evaluate_listening tool
    │
    ▼
listening_evaluation_tool.evaluate_listening(passage, qa_pairs)
    │
    ├─ Calculate basic metrics:
    │  ├─ correct_count
    │  ├─ total_questions
    │  ├─ accuracy_percentage
    │
    ├─ Call LLM for deep analysis:
    │  ├─ Comprehension score
    │  ├─ Understanding level
    │  ├─ Missed key points
    │
    ▼
Structured ListeningEvaluationOutput
    │
    ├─ comprehension_score: 75.0
    ├─ correct_answers: 1
    ├─ total_questions: 2
    ├─ accuracy_percentage: 50.0
    ├─ understanding_level: "fair"
    ├─ missed_key_points: [...]
    ├─ feedback: str
    ├─ recommendations: str
    │
    ▼
Format and Return Response
```

---

## Data Models

### Input Models

```python
GrammarEvaluationRequest:
  - original_passage: str
  - transcribed_text: str

ReadingEvaluationRequest:
  - original_passage: str
  - transcribed_text: str
  - audio_duration_seconds: float
  - min_wpm: Optional[int] = 140
  - max_wpm: Optional[int] = 170

QuestionAnswerPair:
  - question: str
  - candidate_answer: str
  - correct_answer: str

ListeningEvaluationRequest:
  - passage: str
  - questions_and_answers: List[QuestionAnswerPair]
```

### Output Models

```python
GrammarEvaluationOutput:
  - evaluation: GrammarEvaluationResult
    ├─ accuracy_score: float
    ├─ error_count: int
    ├─ error_types: List[str]
    ├─ feedback: str
    └─ overall_assessment: str

ReadingEvaluationOutput:
  - evaluation: ReadingEvaluationResult
    ├─ reading_speed_wpm: float
    ├─ reading_speed_assessment: Literal[...]
    ├─ fluency_score: float
    ├─ pronunciation_accuracy: float
    ├─ overall_score: float
    ├─ feedback: str
    └─ recommendations: str

ListeningEvaluationOutput:
  - evaluation: ListeningEvaluationResult
    ├─ comprehension_score: float
    ├─ correct_answers: int
    ├─ total_questions: int
    ├─ accuracy_percentage: float
    ├─ understanding_level: str
    ├─ missed_key_points: List[str]
    ├─ feedback: str
    └─ recommendations: str

ServiceResponse:
  - message: str
  - evaluation_type: str
  - status: str
  - data: {evaluation: {...}}
```

---

## File Organization

```
question-bank-agent/
├── app/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── evaluation_agent.py       ←── NEW: Main evaluation agent
│   │   ├── qb_agent.py               ←── Existing
│   │   ├── prompts.py                ←── UPDATED: Added evaluation prompts
│   │   └── __pycache__/
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── grammar_evaluation_tool.py ←── NEW: Grammar eval tool
│   │   ├── reading_evaluation_tool.py ←── NEW: Reading eval tool
│   │   ├── listening_evaluation_tool.py ←── NEW: Listening eval tool
│   │   ├── grammar_tool.py            ←── Existing
│   │   ├── comprehension_tool.py      ←── Existing
│   │   ├── validate_question_quality_tool.py ←── Existing
│   │   └── __pycache__/
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── evaluation_service.py      ←── NEW: Evaluation service
│   │   ├── qb_service.py              ←── Existing
│   │   ├── audio_service.py           ←── Existing
│   │   ├── tts_service.py             ←── Existing
│   │   └── __pycache__/
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── evaluation_routes.py       ←── UPDATED: New agentic endpoints
│   │   ├── qb_routes.py               ←── Existing
│   │   ├── audio_routes.py            ←── Existing
│   │   ├── comprehension_passage_routes.py ←── Existing
│   │   └── __pycache__/
│   │
│   ├── db/
│   │   └── ...
│   │
│   ├── models/
│   │   └── ...
│   │
│   └── main.py                        ←── Already includes evaluation router
│
├── EVALUATION_AGENT_API.md            ←── NEW: Complete API reference
├── EVALUATION_AGENT_IMPLEMENTATION.md ←── NEW: Architecture & design docs
├── EVALUATION_AGENT_QUICKSTART.md     ←── NEW: Testing guide
├── ARCHITECTURE_DIAGRAM.md            ←← YOU ARE HERE
│
└── ...existing files...
```

---

## Key Design Patterns

### 1. Tool-Agent-Service-Routes Pattern

```
                Tool
            (Lower Level)
                 │
                 ▼
              Agent
          (Orchestrates)
                 │
                 ▼
             Service
        (Business Logic)
                 │
                 ▼
              Routes
           (API Layer)
```

### 2. Middleware Enforcement

```
Agent Creation
    │
    ├─ Tool 1: Limit 1 call
    ├─ Tool 2: Limit 1 call
    ├─ Tool 3: Limit 1 call
    │
    ├─ Ensure exact 1 tool executes per request
    ├─ Prevent loops and retries
    │
    ▼
Structured Output
```

### 3. Structured Output via LLM

```
Tool Execution
    │
    ├─ Pydantic Model Definition
    ├─ LLM with function_calling method
    │
    ▼
Type-Safe Result
(Automatic parsing)
    │
    ▼
Validation & Response
```

---

## Deployment Considerations

### Memory Usage

- Agent creation: ~50MB
- Per evaluation: negligible
- All operations in-memory (no persistence without DB)

### Latency

- Tool execution: 2-5 seconds (LLM dependent)
- Service layer: <100ms
- Route handling: <50ms
- Total: 2-6 seconds per request

### Concurrency

- Safe for concurrent requests
- No shared state between evaluations
- Each request gets its own agent instance

### Scalability

- Horizontal: Can run multiple app instances
- Vertical: Can increase system resources
- Bottleneck: OpenAI API rate limits
