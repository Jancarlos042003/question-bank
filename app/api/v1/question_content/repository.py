from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.question_content import QuestionContent


class QuestionContentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_question_content_db(self, question_id: int, content_id: int):
        """Obtiene un contenido específico de una pregunta por su ID y el ID de la pregunta."""
        stmt = select(QuestionContent).where(
            QuestionContent.id == content_id,
            QuestionContent.question_id == question_id,
        )
        return self.db.scalar(stmt)

    def get_question_contents_db(self, question_id: int):
        """Obtiene todos los contenidos de una pregunta ordenados por su campo 'order'."""
        stmt = (
            select(QuestionContent)
            .where(QuestionContent.question_id == question_id)
            .order_by(QuestionContent.order)
        )
        return list(self.db.scalars(stmt).all())

    def update_question_content_db(
            self,
            content: QuestionContent,
            label: str | None,
            content_type,
            value: str | None,
            order: int | None,
            question_hash: str,
    ):
        """Actualiza los campos de un contenido de pregunta y el hash de la pregunta asociada."""
        try:
            if label is not None:
                content.label = label
            if content_type is not None:
                content.type = content_type
            if value is not None:
                content.value = value
            if order is not None:
                content.order = order

            self.db.execute(
                update(Question)
                .where(Question.id == content.question_id)
                .values(question_hash=question_hash)
            )
            self.db.commit()
            self.db.refresh(content)
            return content
        except SQLAlchemyError:
            self.db.rollback()
            raise
