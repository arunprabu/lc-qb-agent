from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal
from app.services.qb_service import QuestionBankService

router = APIRouter()
qb_service = QuestionBankService()

class GenerateQuestionRequest(BaseModel):
    topic: str
    difficulty: Literal["beginner", "intermediate", "advanced"]


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/generate-qb")
async def generate_question(request: GenerateQuestionRequest):
    print(f"""
        ROUTES: Received request to generate question for 
        topic: {request.topic} with 
        difficulty: {request.difficulty}""")
    
    # call the execute_agent method from the QuestionBankAgent class
    result = await qb_service.execute_agent(request.topic, request.difficulty)
    return result