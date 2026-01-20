from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentCreate


def create_assessment(db: Session, assessment: AssessmentCreate):
    try:
        new_assessment = Assessment(**assessment.model_dump(exclude_unset=True))

        db.add(new_assessment)
        db.commit()
        db.refresh(new_assessment)

        return new_assessment
    except SQLAlchemyError:
        db.rollback()
        raise ValueError("Error al crear la evaluación")


def get_assessments(db: Session):
    stmt = select(Assessment)

    return db.execute(stmt).scalars().all()
