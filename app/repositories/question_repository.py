import math

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.core.cache import get_cached_count, invalidate_count_cache, set_cached_count
from app.models.choice import Choice
from app.models.question import Question
from app.models.solution import Solution
from app.repositories.pagination import PaginatedResult


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

    def get_questions_db(
            self, page: int, limit: int, view: str
    ) -> PaginatedResult[Question]:
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

        return PaginatedResult(
            total_count=total,
            total_pages=pages,
            current_page=page,
            items_count=len(questions),
            has_prev=has_prev,
            has_next=has_next,
            items=questions,
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

    def delete_question_db(self, question_id: int):
        stmt = select(Question).where(Question.id == question_id)
        db_question = self.db.scalar(stmt)

        if not db_question:
            return None

        try:
            self.db.delete(db_question)
            self.db.commit()
            invalidate_count_cache()
            return db_question
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def question_exists_db(self, question_id: int) -> bool:
        stmt = select(Question.id).where(Question.id == question_id)
        return self.db.scalar(stmt) is not None

    def update_question_fields_db(self, question_id: int, update_data: dict):
        stmt = select(Question).where(Question.id == question_id)
        db_question = self.db.scalar(stmt)

        if not db_question:
            return None

        for key, value in update_data.items():
            setattr(db_question, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_question)
            return db_question
        except SQLAlchemyError:
            self.db.rollback()
            raise
