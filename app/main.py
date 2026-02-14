from fastapi import FastAPI

from app.api.v1.question.router import question_router
from app.api.v1.subtopic.router import subtopic_router
from app.api.v1.topic.router import topic_router
from app.core.exceptions.handlers import register_exception_handlers
from app.core.logging_config import setup_logging
from app.core.middleware import register_middleware
from app.db import base_imports  # noqa: F401

app = FastAPI()

setup_logging()
register_middleware(app)
register_exception_handlers(app)

app.include_router(question_router, prefix="/questions")
app.include_router(topic_router, prefix="/topics")
app.include_router(subtopic_router, prefix="/subtopics")


@app.get("/")
def root():
    return {"message": "Welcome to API"}
