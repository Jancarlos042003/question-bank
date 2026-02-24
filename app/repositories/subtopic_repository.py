from collections.abc import Mapping

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.cache import get_cached_count, set_cached_count
from app.models.subtopic import Subtopic


class SubtopicRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_subtopic(self, subtopic_id: int):
        stmt = select(Subtopic).where(Subtopic.id == subtopic_id)
        return self.db.scalar(stmt)

    def get_subtopics(self, page: int = 1, limit: int = 100):
        offset = (page - 1) * limit

        # OBTENEMOS SUBTEMAS
        stmt = select(Subtopic).offset(offset).limit(limit)
        items = list(self.db.scalars(stmt).all())  # Convertir el Sequence a list

        # OBTENER TOTAL DE CACHÉ
        total = get_cached_count("subtopics:total_count")
        if total is None:
            total = self.db.scalar(select(func.count()).select_from(Subtopic))
            set_cached_count(name="subtopics:total_count", value=total, ttl=300)

        return items, total

    def create_subtopic(self, subtopic_data: Mapping[str, object]):
        db_subtopic = Subtopic(**subtopic_data)
        try:
            self.db.add(db_subtopic)
            self.db.commit()
            self.db.refresh(db_subtopic)
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise
        else:
            return db_subtopic

    def update_subtopic(self, subtopic_id: int, update_data: Mapping[str, object]):
        stmt = select(Subtopic).where(Subtopic.id == subtopic_id)
        db_subtopic = self.db.scalar(stmt)

        if not db_subtopic:
            return None

        for key, value in update_data.items():
            setattr(db_subtopic, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_subtopic)
        except SQLAlchemyError:
            self.db.rollback()
            raise
        else:
            return db_subtopic

    def delete_subtopic(self, subtopic_id: int):
        stmt = select(Subtopic).where(Subtopic.id == subtopic_id)
        db_subtopic = self.db.scalar(stmt)

        if not db_subtopic:
            return None

        try:
            self.db.delete(db_subtopic)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
        else:
            return db_subtopic
