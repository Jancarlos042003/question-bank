import math

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.question.schemas import (
    QuestionCreate,
    QuestionPaginatedResponse,
    QuestionSimpleStudyResponse,
)
from app.models.question import Question


def create_question_db(db: Session, question: QuestionCreate):
    """Crea una pregunta en la BD. Sin lógica de negocio."""
    new_question = Question(**question.model_dump())
    db.add(new_question)
    db.flush()  # obtiene ID sin commit

    return new_question


def get_questions_db(db: Session, page: int, limit: int):
    offset = (page - 1) * limit

    stmt = (
        select(Question)
        .order_by(Question.id)
        .limit(limit)
        .offset(offset)
        .options(
            selectinload(Question.choices),
            selectinload(Question.contents),
            selectinload(Question.solution),
        )
    )

    # Obtener preguntas
    items = list(db.scalars(stmt).all())  # Convertir el Sequence a list

    # Obtener total
    total = db.scalar(select(func.count()).select_from(Question))

    # Calcular número de páginas
    pages = math.ceil(total / limit)

    has_next = page < pages
    has_prev = page > 1

    return QuestionPaginatedResponse(
        total_count=total,
        total_pages=pages,
        current_page=page,
        items_count=len(items),
        has_prev=has_prev,
        has_next=has_next,
        items=items,
    )
