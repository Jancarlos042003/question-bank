import math

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.api.v1.question.schemas import (
    QuestionSummaryPublic,
    QuestionPaginatedSummaryResponse,
    QuestionDetailPublic,
    QuestionPaginatedDetailResponse,
)
from app.core.cache import get_cached_count, set_cached_count
from app.models.choice import Choice
from app.models.question import Question
from app.models.solution import Solution


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_question_db(self, question: Question):
        """Crea una pregunta en la BD"""
        try:
            self.db.add(question)
            self.db.commit()
            self.db.refresh(question)

        # No se necesita capturar IntegrityError porque ya hereda de SQLAlchemyError
        except SQLAlchemyError:
            self.db.rollback()
            raise
        else:
            return question

    def get_questions_db(self, page: int, limit: int, view: str):
        offset = (page - 1) * limit

        if view == "summary":
            stmt = select(Question).order_by(Question.id).limit(limit).offset(offset)
        else:
            stmt = (
                select(Question)
                .order_by(Question.id)
                .limit(limit)
                .offset(offset)
                .options(
                    selectinload(Question.choices).selectinload(Choice.contents),
                    selectinload(Question.solutions).selectinload(Solution.contents),
                )
            )

        # Obtener preguntas
        questions = list(self.db.scalars(stmt).all())  # Convertir el Sequence a list

        # Obtener total
        # Intentar obtener del cache
        total = get_cached_count()
        if total is None:
            # Si no está en cache, consultar BD
            total = self.db.scalar(select(func.count()).select_from(Question))
            # Guardar en cache por 5 minutos
            set_cached_count(count=total, ttl=300)

        # Calcular número de páginas
        pages = math.ceil(total / limit)

        has_next = page < pages
        has_prev = page > 1

        if view == "summary":
            items = [QuestionSummaryPublic.model_validate(q) for q in questions]
            return QuestionPaginatedSummaryResponse(
                total_count=total,
                total_pages=pages,
                current_page=page,
                items_count=len(items),
                has_prev=has_prev,
                has_next=has_next,
                items=items,
            )

        items = [QuestionDetailPublic.model_validate(q) for q in questions]
        return QuestionPaginatedDetailResponse(
            total_count=total,
            total_pages=pages,
            current_page=page,
            items_count=len(items),
            has_prev=has_prev,
            has_next=has_next,
            items=items,
        )

    def get_question_db(self, question_id: int, view: str):
        if view == "summary":
            stmt = select(Question).where(Question.id == question_id)

        else:
            stmt = (
                select(Question)
                .where(Question.id == question_id)
                .options(
                    selectinload(Question.choices).selectinload(Choice.contents),
                    selectinload(Question.solutions).selectinload(Solution.contents),
                )
            )

        return self.db.scalar(stmt)
