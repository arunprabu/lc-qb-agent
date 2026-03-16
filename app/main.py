from fastapi import FastAPI
import os 
from app.routes.qb_routes import router as questions_router
from app.routes.audio_routes import router as audio_router
from app.routes.comprehension_passage_routes import router as comprehension_passage_router
from app.routes.evaluation_routes import router as evaluation_router

app = FastAPI(title="Question Bank Agent", version="1.0")
app.include_router(questions_router, prefix="/api/v1/questions")
app.include_router(audio_router, prefix="/api/v1/audio")
app.include_router(comprehension_passage_router, prefix="/api/v1/passage")

app.include_router(evaluation_router, prefix="/api/v1/candidates")
