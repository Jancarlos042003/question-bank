from fastapi import FastAPI

from app.core.middleware import register_middleware
from app.db.engine import
from app.routers.assessment import assessment_router
from app.routers.question import question_router

app = FastAPI()

register_middleware(app)

app.include_router(question_router, prefix="/questions")
app.include_router(assessment_router, prefix="/assessments")


@app.get("/")
def root():
    return {"message": "Welcome to API"}
