from sqlalchemy import select, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.core.cache import invalidate_count_cache, get_cached_count, set_cached_count
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

            invalidate_count_cache("questions:total_count")

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

        # GUARDAR EL TOTAL DE PREGUNTAS EN CACHÉ
        # Intentar obtener del cache
        total = get_cached_count(name="questions:total_count")
        if total is None:
            # Si no está en cache, consultar BD
            total = self.db.scalar(select(func.count()).select_from(Question))
            # Guardar en cache por 5 minutos
            set_cached_count(name="questions:total_count", value=total, ttl=300)

        # Obtener preguntas
        return list(self.db.scalars(stmt).all())  # Convertir el Sequence a list

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

    def delete_question_db(self, question_id: int) -> bool:
        stmt = delete(Question).where(Question.id == question_id).returning(Question.id)

        try:
            deleted_id = self.db.execute(stmt).scalar_one_or_none()
            if deleted_id is None:
                return False

            self.db.commit()
            invalidate_count_cache("questions:total_count")
            return True
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def question_exists_db(self, question_id: int) -> bool:
        stmt = select(Question.id).where(Question.id == question_id)
        return self.db.scalar(stmt) is not None

    def update_question_fields_db(self, question_id: int, update_data: dict):
        """Actualiza los campos areas, difficulty, question type, subtopic de una pregunta en la BD"""
        stmt = select(Question).where(Question.id == question_id)
        db_question = self.db.scalar(stmt)

        if not db_question:
            return None

        for key, value in update_data.items():
            setattr(db_question, key, value)

        try:
            self.db.commit()
            # No se realizan un refresh ni se retorna nada ya que se devuelve un estado 204
        except SQLAlchemyError:
            self.db.rollback()
            raise
