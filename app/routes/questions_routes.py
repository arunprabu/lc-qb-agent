from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

router = APIRouter()

class GenerateQuestionRequest(BaseModel):
    topic: str
    difficulty: Literal["beginner", "intermediate", "advanced"]


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/generate-qb")
async def generate_question(request: GenerateQuestionRequest):
    print(f"Received request to generate question for topic: {request.topic} with difficulty: {request.difficulty}")
    return {"message": "Question generation complete", "topic": request.topic, "difficulty": request.difficulty }