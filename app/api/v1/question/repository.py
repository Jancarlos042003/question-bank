import math

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.v1.question.schemas import QuestionPaginatedResponse
from app.core.exceptions.domain import DuplicateQuestionHashError
from app.models.question import Question


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_question_db(self, question: Question):
        """Crea una pregunta en la BD"""
        stmt = select(Question).where(Question.question_hash == question.question_hash)
        existing = self.db.scalar(stmt)

        if existing:
            raise DuplicateQuestionHashError

        try:
            self.db.add(question)
            self.db.commit()
            self.db.refresh(question)
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise
        else:
            return question

    def get_questions_db(self, page: int, limit: int):
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
        items = list(self.db.scalars(stmt).all())  # Convertir el Sequence a list

        # Obtener total
        total = self.db.scalar(select(func.count()).select_from(Question))

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
