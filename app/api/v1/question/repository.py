from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.question.schemas import QuestionCreate
from app.models.question import Question


def create_question_db(db: Session, question: QuestionCreate):
    """Crea una pregunta en la BD. Sin lógica de negocio."""
    new_question = Question(**question.model_dump())
    db.add(new_question)
    db.flush()  # obtiene ID sin commit

    return new_question


def get_all_questions_db(db: Session):
    stmt = select(Question)
    return db.execute(stmt).scalars().all()
