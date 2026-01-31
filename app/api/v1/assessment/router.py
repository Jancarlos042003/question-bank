from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.assessment.repository import create_assessment, get_assessments
from app.api.v1.assessment.schemas import AssessmentCreate, AssessmentRead
from app.db.session import get_session

assessment_router = APIRouter()


@assessment_router.post(
    "", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED
)
def add_assessment(
    db: Annotated[Session, Depends(get_session)], assessment: AssessmentCreate
):
    return create_assessment(db, assessment)


@assessment_router.get("", response_model=list[AssessmentRead])
def all_assessments(db: Annotated[Session, Depends(get_session)]):
    return get_assessments(db)
