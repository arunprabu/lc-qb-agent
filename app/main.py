from fastapi import FastAPI
import os 
from app.routes.qb_routes import router as questions_router
from app.routes.audio_routes import router as audio_router

app = FastAPI(title="Question Bank Agent", version="1.0")
app.include_router(questions_router, prefix="/api/v1")
app.include_router(audio_router, prefix="/api/v1/audio")
