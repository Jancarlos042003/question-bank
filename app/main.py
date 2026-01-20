from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.db.base_imports
from app.db.base import Base
from app.db.engine import engine
from app.routers.assessment import assessment_router
from app.routers.question import question_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(question_router, prefix="/questions")
app.include_router(assessment_router, prefix="/assessments")


@app.get("/")
def root():
    return {"message": "Welcome to API"}
