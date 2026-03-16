# Evaluation Agent - Quick Start Guide

## 1. Prerequisites

Ensure the application is running:

```bash
cd /Users/arun/Documents/RamSELabs/CorporateTraining/CourseMaterials/hexaware/agentic-ai-course-mar2026/question-bank-agent
uv run uvicorn main.app:app --host 0.0.0.0 --port 8000
```

Verify endpoint is accessible:

```bash
curl http://localhost:8000/api/v1/health
```

## 2. Quick Test Examples

### Test 1: Grammar Evaluation

```bash
curl -X POST "http://localhost:8000/api/v1/candidates/agentic-evaluation/grammar" \
  -H "Content-Type: application/json" \
  -d '{
    "original_passage": "The quick brown fox jumps over the lazy dog. This is an important sentence for testing grammar evaluation.",
    "transcribed_text": "The quick brown fox jumps over a lazy dog. This is important sentence for testing grammar evaluation."
  }'
```

**Expected Response**:

```json
{
  "message": "Evaluation completed successfully",
  "evaluation_type": "grammar",
  "status": "success",
  "data": {
    "evaluation": {
      "accuracy_score": 85.5,
      "error_count": 2,
      "error_types": ["article_error", "word_substitution"],
      "feedback": "Minor errors with articles and word choice.",
      "overall_assessment": "Good grammar with minor improvements needed"
    }
  }
}
```

### Test 2: Reading Evaluation

```bash
curl -X POST "http://localhost:8000/api/v1/candidates/agentic-evaluation/reading" \
  -H "Content-Type: application/json" \
  -d '{
    "original_passage": "Climate change refers to significant changes in global temperatures and weather patterns over time. While climate change is a natural phenomenon that has occurred throughout Earth'\''s history, human activities have become a major driver of recent changes.",
    "transcribed_text": "Climate change refers to significant changes in global temperatures and weather patterns over time. While climate change is a natural phenomenon that has occurred throughout Earth'\''s history, human activities have been a major driver of recent changes.",
    "audio_duration_seconds": 30,
    "min_wpm": 140,
    "max_wpm": 170
  }'
```

**Expected Response**:

```json
{
  "message": "Evaluation completed successfully",
  "evaluation_type": "reading",
  "status": "success",
  "data": {
    "evaluation": {
      "reading_speed_wpm": 152.5,
      "reading_speed_assessment": "average",
      "fluency_score": 82.0,
      "pronunciation_accuracy": 88.5,
      "overall_score": 85.2,
      "feedback": "Good reading speed within the expected range. Speech was clear and well-paced.",
      "recommendations": "Continue to maintain consistent reading pace. Further improvements in pronunciation of compound words would be beneficial."
    }
  }
}
```

### Test 3: Listening Evaluation

```bash
curl -X POST "http://localhost:8000/api/v1/candidates/agentic-evaluation/listening" \
  -H "Content-Type: application/json" \
  -d '{
    "passage": "Paris is the capital of France. It is known for the Eiffel Tower, Notre-Dame Cathedral, and world-class museums. The city attracts millions of tourists annually.",
    "questions_and_answers": [
      {
        "question": "What is the capital of France?",
        "candidate_answer": "Paris",
        "correct_answer": "Paris"
      },
      {
        "question": "What is Paris known for?",
        "candidate_answer": "The Eiffel Tower and museums",
        "correct_answer": "The Eiffel Tower, Notre-Dame Cathedral, and world-class museums"
      },
      {
        "question": "How many tourists visit Paris annually?",
        "candidate_answer": "I do not know",
        "correct_answer": "Millions"
      }
    ]
  }'
```

**Expected Response**:

```json
{
  "message": "Evaluation completed successfully",
  "evaluation_type": "listening",
  "status": "success",
  "data": {
    "evaluation": {
      "comprehension_score": 50.0,
      "correct_answers": 1,
      "total_questions": 3,
      "accuracy_percentage": 33.33,
      "understanding_level": "poor",
      "missed_key_points": [
        "Specific tourist numbers information",
        "All cultural landmarks (missed Notre-Dame)"
      ],
      "feedback": "Candidate demonstrates partial listening comprehension with understanding of some main ideas.",
      "recommendations": "Focus on capturing all mentioned details and specific information. Practice note-taking while listening."
    }
  }
}
```

## 3. Integration with Your Application

### Option A: Use in a Web Interface

```javascript
// JavaScript/Frontend example
async function evaluateCandidate() {
  const response = await fetch(
    "http://localhost:8000/api/v1/candidates/agentic-evaluation/grammar",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        original_passage: "...",
        transcribed_text: "...",
      }),
    },
  );
  const result = await response.json();
  console.log(result);
}
```

### Option B: Use in Python

```python
import httpx
import asyncio

async def evaluate():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:8000/api/v1/candidates/agentic-evaluation/grammar',
            json={
                'original_passage': '...',
                'transcribed_text': '...'
            }
        )
        return response.json()

result = asyncio.run(evaluate())
```

### Option C: Use Internally (Direct Python Call)

```python
from app.services.evaluation_service import EvaluationService

service = EvaluationService()
result = await service.execute_evaluation(
    'grammar',
    original_passage='...',
    transcribed_text='...'
)
```

## 4. Understanding Response Formats

### Error Response

If something goes wrong:

```json
{
  "error": "Detailed error message describing what went wrong",
  "evaluation_type": "grammar"
}
```

### Check Logs

To debug issues, check the application logs:

```bash
# Look for these log messages
ROUTES: Received agentic evaluation request for grammar
EVALUATION_SERVICE: Executing evaluation for type: grammar
EVALUATION_AGENT: Running agent for evaluation type: grammar
TOOL: Evaluating grammar - comparing original vs transcribed text
```

## 5. Customization Options

### Adjust Reading Speed Parameters

```bash
# Custom WPM ranges (example: slower speech evaluation)
curl -X POST "http://localhost:8000/api/v1/candidates/agentic-evaluation/reading" \
  -H "Content-Type: application/json" \
  -d '{
    "original_passage": "...",
    "transcribed_text": "...",
    "audio_duration_seconds": 60,
    "min_wpm": 100,
    "max_wpm": 140
  }'
```

### Add More Q&A Pairs

For listening evaluation, add as many Q&A pairs as needed:

```json
{
  "passage": "...",
  "questions_and_answers": [
    {"question": "Q1", "candidate_answer": "A1", "correct_answer": "C1"},
    {"question": "Q2", "candidate_answer": "A2", "correct_answer": "C2"},
    {"question": "Q3", "candidate_answer": "A3", "correct_answer": "C3"},
    ...more questions...
  ]
}
```

## 6. Performance Considerations

- **Response Time**: Typically 2-5 seconds per evaluation (depends on LLM latency)
- **Token Usage**: ~500-1000 tokens per evaluation (varies by passage length)
- **Concurrent Requests**: Safe to handle multiple simultaneous evaluations
- **API Rate Limits**: Subject to OpenAI rate limits

## 7. Troubleshooting

### Issue: Module not found errors

**Solution**: Ensure all files are in correct locations and imports are correct

```bash
# Verify files exist
ls -la app/tools/grammar_evaluation_tool.py
ls -la app/tools/reading_evaluation_tool.py
ls -la app/tools/listening_evaluation_tool.py
ls -la app/agent/evaluation_agent.py
ls -la app/services/evaluation_service.py
```

### Issue: OpenAI API errors

**Solution**: Check API key and quota

```bash
# Verify .env has OPENAI_API_KEY set
grep OPENAI_API_KEY .env
```

### Issue: Slow responses

**Solution**: Check network connectivity and OpenAI API status

### Issue: Unexpected evaluation results

**Solution**: Check the feedback in response - it includes detailed analysis from the LLM

## 8. Documentation

For detailed API documentation, see: [EVALUATION_AGENT_API.md](./EVALUATION_AGENT_API.md)

For implementation details, see: [EVALUATION_AGENT_IMPLEMENTATION.md](./EVALUATION_AGENT_IMPLEMENTATION.md)

## 9. Next Steps

1. ✅ Test all three evaluation types
2. ✅ Integrate with your frontend/application
3. ✅ Monitor evaluation quality and refine prompts if needed
4. ⏳ Add database persistence (optional)
5. ⏳ Create evaluation dashboard (optional)
6. ⏳ Implement batch evaluation (optional)

---

**Questions?** Check the documentation files or review the source code in:

- `app/tools/` - Evaluation tool implementations
- `app/agent/evaluation_agent.py` - LangChain agent
- `app/services/evaluation_service.py` - Service layer
- `app/routes/evaluation_routes.py` - API routes
