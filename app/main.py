from fastapi import FastAPI

from app.api.v1.assessment.router import assessment_router
from app.api.v1.question.router import question_router
from app.core.middleware import register_middleware
from app.db import base_imports

app = FastAPI()

register_middleware(app)

app.include_router(question_router, prefix="/questions")
app.include_router(assessment_router, prefix="/assessments")


@app.get("/")
def root():
    return {"message": "Welcome to API"}
