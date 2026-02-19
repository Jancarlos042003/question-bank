from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.question_source import QuestionSource


class QuestionSourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_question_source_db(self, question_id: int, question_source_id: int):
        stmt = select(QuestionSource).where(
            QuestionSource.id == question_source_id,
            QuestionSource.question_id == question_id,
        )
        return self.db.scalar(stmt)

    def update_question_source_db(
        self,
        question_source: QuestionSource,
        source_id: int | None,
        page: int | None,
    ):
        if source_id is not None:
            question_source.source_id = source_id
        if page is not None:
            question_source.page = page

        try:
            self.db.commit()
            self.db.refresh(question_source)
            return question_source
        except SQLAlchemyError:
            self.db.rollback()
            raise
