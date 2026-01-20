from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.assessment import create_assessment, get_assessments
from app.db.dep import get_db
from app.schemas.assessment import AssessmentRead, AssessmentCreate

assessment_router = APIRouter()


@assessment_router.post("", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED)
def add_assessment(db: Annotated[Session, Depends(get_db)], assessment: AssessmentCreate):
    return create_assessment(db, assessment)


@assessment_router.get("", response_model=list[AssessmentRead])
def all_assessments(db: Annotated[Session, Depends(get_db)]):
    return get_assessments(db)
