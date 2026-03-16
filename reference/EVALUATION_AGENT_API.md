# Evaluation Agent API Reference

## Overview

The Evaluation Agent is an agentic system that evaluates candidates' English language skills across three domains:

- **Grammar**: Assess grammar accuracy by comparing transcribed text with original passage
- **Reading**: Assess reading speed (WPM), fluency, and pronunciation accuracy
- **Listening**: Assess listening comprehension based on Q&A responses

## Architecture

The evaluation agent follows the same pattern as the QuestionBank Agent:

```
Routes → Service → Agent → Tools
   ↓        ↓        ↓      ↓
POST   execute_  run_evaluation  evaluate_grammar/
endpoints  evaluation_agent  reading/listening
```

### Components

1. **Tools** (`app/tools/`):
   - `grammar_evaluation_tool.py` - Evaluates grammar accuracy
   - `reading_evaluation_tool.py` - Evaluates reading speed & fluency
   - `listening_evaluation_tool.py` - Evaluates listening comprehension

2. **Agent** (`app/agent/`):
   - `evaluation_agent.py` - Orchestrates tools using LangChain
   - Uses ToolCallLimitMiddleware to ensure 1 tool call per request
   - Returns structured EvaluationOutput

3. **Service** (`app/services/`):
   - `evaluation_service.py` - Calls evaluation agent
   - Handles parameter passing and result formatting

4. **Routes** (`app/routes/`):
   - `evaluation_routes.py` - Exposes HTTP endpoints

## API Endpoints

### Base URL

```
http://localhost:8000/api/v1/candidates
```

### 1. Grammar Evaluation

**Endpoint**: `POST /agentic-evaluation/grammar`

**Description**: Evaluate candidate's grammar by comparing their transcription with the original passage.

**Request Body**:

```json
{
  "original_passage": "The complete passage that should be read...",
  "transcribed_text": "What the candidate actually said/transcribed..."
}
```

**Example**:

```bash
curl -X POST "http://localhost:8000/api/v1/candidates/agentic-evaluation/grammar" \
  -H "Content-Type: application/json" \
  -d {
    "original_passage": "Climate change refers to significant changes in global temperatures and weather patterns over time.",
    "transcribed_text": "Climate change is about significant changes in global temperatures and weather patterns."
  }
```

**Response**:

```json
{
  "message": "Evaluation completed successfully",
  "evaluation_type": "grammar",
  "status": "success",
  "data": {
    "evaluation": {
      "accuracy_score": 85.5,
      "error_count": 2,
      "error_types": ["word_substitution", "word_omission"],
      "feedback": "Minor differences in wording, but grammatically correct.",
      "overall_assessment": "Good Grammar - Minor refinements needed"
    }
  }
}
```

---

### 2. Reading Evaluation

**Endpoint**: `POST /agentic-evaluation/reading`

**Description**: Evaluate candidate's reading skills based on speed (WPM), fluency, and pronunciation accuracy.

**Request Body**:

```json
{
  "original_passage": "The passage to be read...",
  "transcribed_text": "The transcribed version of what was spoken...",
  "audio_duration_seconds": 120,
  "min_wpm": 140,
  "max_wpm": 170
}
```

**Parameters**:

- `original_passage` (string): The passage that should be read
- `transcribed_text` (string): Transcription of candidate's speech
- `audio_duration_seconds` (float): Duration of audio in seconds
- `min_wpm` (integer, optional): Minimum acceptable WPM (default: 140)
- `max_wpm` (integer, optional): Maximum acceptable WPM (default: 170)

**Example**:

```bash
curl -X POST "http://localhost:8000/api/v1/candidates/agentic-evaluation/reading" \
  -H "Content-Type: application/json" \
  -d {
    "original_passage": "Climate change refers to...",
    "transcribed_text": "Climate change is about...",
    "audio_duration_seconds": 65,
    "min_wpm": 140,
    "max_wpm": 170
  }
```

**Response**:

```json
{
  "message": "Evaluation completed successfully",
  "evaluation_type": "reading",
  "status": "success",
  "data": {
    "evaluation": {
      "reading_speed_wpm": 155.5,
      "reading_speed_assessment": "average",
      "fluency_score": 78.0,
      "pronunciation_accuracy": 82.5,
      "overall_score": 80.2,
      "feedback": "Good reading speed within the expected range.",
      "recommendations": "Focus on maintaining consistent pace and clearer pronunciation of technical terms."
    }
  }
}
```

---

### 3. Listening Evaluation

**Endpoint**: `POST /agentic-evaluation/listening`

**Description**: Evaluate candidate's listening comprehension based on their answers to questions about a passage.

**Request Body**:

```json
{
  "passage": "The passage that was listened to...",
  "questions_and_answers": [
    {
      "question": "What is climate change?",
      "candidate_answer": "Changes in global temperatures",
      "correct_answer": "Changes in global temperatures and weather patterns"
    },
    {
      "question": "What causes global warming?",
      "candidate_answer": "Burning fossil fuels and deforestation",
      "correct_answer": "Burning fossil fuels and deforestation"
    }
  ]
}
```

**Parameters**:

- `passage` (string): The passage that was listened to
- `questions_and_answers` (array): List of Q&A objects with:
  - `question` (string): The question asked
  - `candidate_answer` (string): Answer provided by candidate
  - `correct_answer` (string): The correct/expected answer

> **Note**: `correct_answers`, `total_questions`, and `accuracy_percentage` are computed deterministically by exact string match (case-insensitive) in the tool — they are **not** generated by the LLM. The LLM only provides `comprehension_score`, `understanding_level`, `missed_key_points`, `feedback`, and `recommendations`.

**Example**:

```bash
curl -X POST "http://localhost:8000/api/v1/candidates/agentic-evaluation/listening" \
  -H "Content-Type: application/json" \
  -d {
    "passage": "Climate change refers to significant changes...",
    "questions_and_answers": [
      {
        "question": "What is climate change?",
        "candidate_answer": "Changes in global temperatures",
        "correct_answer": "Changes in global temperatures and weather patterns"
      }
    ]
  }
```

**Response**:

```json
{
  "message": "Evaluation completed successfully",
  "evaluation_type": "listening",
  "status": "success",
  "data": {
    "evaluation": {
      "comprehension_score": 75.0,
      "correct_answers": 1,
      "total_questions": 2,
      "accuracy_percentage": 50.0,
      "understanding_level": "fair",
      "missed_key_points": [
        "Impact of climate change on ecosystems",
        "Global action required for mitigation"
      ],
      "feedback": "Candidate demonstrates partial understanding of the passage.",
      "recommendations": "Focus on identifying supporting details and key concepts in listening texts."
    }
  }
}
```

---

## Legacy Endpoints (Backward Compatibility)

The following legacy endpoints are still available:

- `POST /api/v1/candidates/evaluation/grammar` - Grammar evaluation (POST with GrammarEvaluationRequest)
- `POST /api/v1/candidates/evaluation/reading` - Reading evaluation (POST with ReadingEvaluationRequest)
- `POST /api/v1/candidates/evaluation/listening` - Listening evaluation (POST with ListeningEvaluationRequest)

---

## Request Model Definitions

### GrammarEvaluationRequest

```python
class GrammarEvaluationRequest(BaseModel):
    original_passage: str
    transcribed_text: str
```

### ReadingEvaluationRequest

```python
class ReadingEvaluationRequest(BaseModel):
    original_passage: str
    transcribed_text: str
    audio_duration_seconds: float
    min_wpm: Optional[int] = 140
    max_wpm: Optional[int] = 170
```

### ListeningEvaluationRequest

```python
class QuestionAnswerPair(BaseModel):
    question: str
    candidate_answer: str
    correct_answer: str

class ListeningEvaluationRequest(BaseModel):
    passage: str
    questions_and_answers: List[QuestionAnswerPair]
```

---

## Response Model

All evaluation endpoints return the following structure:

```python
{
  "message": str,  # "Evaluation completed successfully"
  "evaluation_type": str,  # "grammar", "reading", or "listening"
  "status": str,  # "success" or error status
  "data": {
    "evaluation": {
      # Specific evaluation results based on type
    }
  }
}
```

---

## Implementation Details

### Running the Evaluation Agent

From `evaluation_agent.py`:

```python
async def run_evaluation_agent(evaluation_type: str, **kwargs):
    """
    Run the evaluation agent for the specified evaluation type.

    Args:
        evaluation_type: "grammar", "reading", or "listening"
        **kwargs: Additional parameters specific to evaluation type:
            - Grammar: original_passage, transcribed_text
            - Reading: original_passage, transcribed_text, audio_duration_seconds
            - Listening: passage, questions_and_answers (List[dict])

    Returns:
        dict: Evaluation results
    """
```

### Tool Specifications

All tools use:

- **Model**: `gpt-4o-mini`
- **Max Tokens**: Configurable via `MAX_TOKENS_FROM_TOOLS` env var (default: 1500)
- **Temperature**: 0.3 (lower for more consistent evaluations)
- **Middleware**: ToolCallLimitMiddleware ensures single tool execution

---

## Error Handling

If an error occurs, the response will include:

```json
{
  "error": "Detailed error message",
  "evaluation_type": "grammar|reading|listening"
}
```

---

## Integration with Existing System

The evaluation agent integrates seamlessly with the existing question bank system:

- Uses same LangChain/OpenAI infrastructure
- Follows same agent pattern (tools → agent → service → routes)
- Compatible with existing database models if needed
- Respects same environment configuration (.env.example)

---

## Testing

Test from command line or Postman:

```bash
# Test Grammar Evaluation
curl -X POST "http://localhost:8000/api/v1/candidates/agentic-evaluation/grammar" \
  -H "Content-Type: application/json" \
  -d '{
    "original_passage": "The quick brown fox jumps over the lazy dog.",
    "transcribed_text": "The quick brown fox jumps over the lazy dog."
  }'

# Test Reading Evaluation
curl -X POST "http://localhost:8000/api/v1/candidates/agentic-evaluation/reading" \
  -H "Content-Type: application/json" \
  -d '{
    "original_passage": "The quick brown fox jumps over the lazy dog.",
    "transcribed_text": "The quick brown fox jumps over the lazy dog.",
    "audio_duration_seconds": 5
  }'

# Test Listening Evaluation
curl -X POST "http://localhost:8000/api/v1/candidates/agentic-evaluation/listening" \
  -H "Content-Type: application/json" \
  -d '{
    "passage": "Paris is the capital of France.",
    "questions_and_answers": [
      {
        "question": "What is the capital of France?",
        "candidate_answer": "Paris",
        "correct_answer": "Paris"
      }
    ]
  }'
```

---

## Architecture Diagram

```
Client
  ↓
POST /api/v1/candidates/agentic-evaluation/grammar
  ↓
evaluation_routes.py (agentic_evaluation_with_grammar)
  ↓
evaluation_service.execute_evaluation()
  ↓
evaluation_agent.run_evaluation_agent()
  ↓
LangChain Agent with Tools
  ├─ grammar_evaluation_tool
  ├─ reading_evaluation_tool
  └─ listening_evaluation_tool
  ↓
LLM (gpt-4o-mini)
  ↓
Structured Output
  ↓
Response to Client
```

---

## Configuration

**Environment Variables** (from .env.example):

- `OPENAI_API_KEY` - OpenAI API key
- `MAX_TOKENS_FROM_TOOLS` - Maximum tokens from tool calls (default: 1500)

**Database** (optional):
Can be integrated with existing database models if persistence is needed.

---

## Notes

- Each evaluation request triggers exactly ONE tool call (enforced by middleware)
- Results are immediate and synchronous
- Tools use OpenAI's function calling for structured outputs
- All timestamps and metrics are calculated in real-time
- Evaluation scores are normalized to 0-100 range
