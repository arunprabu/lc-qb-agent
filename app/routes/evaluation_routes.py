from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal, List, Optional
from app.services.evaluation_service import EvaluationService

router = APIRouter()
evaluation_service = EvaluationService()


# Request models for agentic evaluation endpoint
class GrammarEvaluationRequest(BaseModel):
    original_passage: str
    transcribed_text: str


class ReadingEvaluationRequest(BaseModel):
    original_passage: str
    transcribed_text: str
    audio_duration_seconds: float
    min_wpm: Optional[int] = 140
    max_wpm: Optional[int] = 170


class QuestionAnswerPair(BaseModel):
    question: str
    candidate_answer: str
    correct_answer: str


class ListeningEvaluationRequest(BaseModel):
    passage: str
    questions_and_answers: List[QuestionAnswerPair]


# New unified agentic evaluation endpoint
@router.post("/agentic-evaluation/grammar")
async def agentic_evaluation_with_grammar(request: GrammarEvaluationRequest):
    """
    Agentic evaluation endpoint for grammar assessment.
    
    Request body:
    {
        "original_passage": "string",
        "transcribed_text": "string"
    }
    """
    print(f"ROUTES: Received agentic evaluation request for grammar")
    
    result = await evaluation_service.execute_evaluation(
        "grammar",
        original_passage=request.original_passage,
        transcribed_text=request.transcribed_text
    )
    return result


@router.post("/agentic-evaluation/reading")
async def agentic_evaluation_reading(request: ReadingEvaluationRequest):
    """
    Agentic evaluation endpoint for reading assessment.
    
    Request body:
    {
        "original_passage": "string",
        "transcribed_text": "string",
        "audio_duration_seconds": float,
        "min_wpm": 140,
        "max_wpm": 170
    }
    """
    print(f"ROUTES: Received agentic evaluation request for reading")
    
    result = await evaluation_service.execute_evaluation(
        "reading",
        original_passage=request.original_passage,
        transcribed_text=request.transcribed_text,
        audio_duration_seconds=request.audio_duration_seconds,
        min_wpm=request.min_wpm,
        max_wpm=request.max_wpm
    )
    return result


@router.post("/agentic-evaluation/listening")
async def agentic_evaluation_listening(request: ListeningEvaluationRequest):
    """
    Agentic evaluation endpoint for listening assessment.
    
    Request body:
    {
        "passage": "string",
        "questions_and_answers": [
            {
                "question": "string",
                "candidate_answer": "string",
                "correct_answer": "string"
            }
        ]
    }
    """
    print(f"ROUTES: Received agentic evaluation request for listening")
    
    result = await evaluation_service.execute_evaluation(
        "listening",
        passage=request.passage,
        questions_and_answers=[qa.model_dump() for qa in request.questions_and_answers]
    )
    return result





# # Legacy endpoints (kept for backward compatibility)
# @router.post("/evaluation/grammar")
# async def grammar_evaluation(request: GrammarEvaluationRequest):
#     """Legacy grammar evaluation endpoint"""
#     return await evaluation_service.execute_evaluation(
#         "grammar",
#         original_passage=request.original_passage,
#         transcribed_text=request.transcribed_text
#     )


# @router.post("/evaluation/reading")
# async def reading_evaluation(request: ReadingEvaluationRequest):
#     """Legacy reading evaluation endpoint"""
#     return await evaluation_service.execute_evaluation(
#         "reading",
#         original_passage=request.original_passage,
#         transcribed_text=request.transcribed_text,
#         audio_duration_seconds=request.audio_duration_seconds,
#         min_wpm=request.min_wpm,
#         max_wpm=request.max_wpm
#     )


# @router.post("/evaluation/listening")
# async def listening_evaluation(request: ListeningEvaluationRequest):
#     """Legacy listening evaluation endpoint"""
#     return await evaluation_service.execute_evaluation(
#         "listening",
#         passage=request.passage,
#         questions_and_answers=[qa.model_dump() for qa in request.questions_and_answers]
#     )



