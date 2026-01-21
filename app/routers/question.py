from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.question import create_question, get_all_questions
from app.db.dep import get_db
from app.schemas.question import QuestionCreate, QuestionRead

question_router = APIRouter()


@question_router.post(
    "", response_model=QuestionRead, status_code=status.HTTP_201_CREATED
)
def add_question(question: QuestionCreate, db: Annotated[Session, Depends(get_db)]):
    return create_question(db, question)


@question_router.get("", response_model=list[QuestionRead])
def all_questions(db: Annotated[Session, Depends(get_db)]):
    return get_all_questions(db)
