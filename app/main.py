from fastapi import FastAPI
import os 
from app.routes.qb_routes import router as questions_router

app = FastAPI(title="Question Bank Agent", version="1.0")
app.include_router(questions_router, prefix="/api/v1")
