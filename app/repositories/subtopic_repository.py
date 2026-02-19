import math

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.subtopic.schemas import (
    SubtopicCreate,
    SubtopicPaginatedResponse,
    SubtopicUpdate,
)
from app.models.subtopic import Subtopic


class SubtopicRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_subtopic(self, subtopic_id: int):
        stmt = select(Subtopic).where(Subtopic.id == subtopic_id)
        return self.db.scalar(stmt)

    def get_subtopics(self, page: int = 0, limit: int = 100):
        offset = (page - 1) * limit

        # OBTENEMOS SUBTEMAS
        stmt = select(Subtopic).offset(offset).limit(limit)
        items = list(self.db.scalars(stmt).all())  # Convertir el Sequence a list

        # TOTAL DE SUBTEMAS
        total = self.db.scalar(select(func.count()).select_from(Subtopic))

        # CANTIDAD DE PÁGINAS
        # Garantizar que siempre exista al menos una página
        # incluso cuando no haya registros (total = 0)
        total_pages = max(1, math.ceil(total / limit))

        has_prev = page > 1
        has_next = page < total_pages

        return SubtopicPaginatedResponse(
            total_pages=total_pages,
            total_count=total,
            current_page=page,
            items_count=len(items),
            has_prev=has_prev,
            has_next=has_next,
            items=items,
        )

    def create_subtopic(self, subtopic: SubtopicCreate):
        db_subtopic = Subtopic(name=subtopic.name, topic_id=subtopic.topic_id)
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

    def update_subtopic(self, subtopic_id: int, subtopic: SubtopicUpdate):
        stmt = select(Subtopic).where(Subtopic.id == subtopic_id)
        db_subtopic = self.db.scalar(stmt)

        if not db_subtopic:
            return None

        # Actualizar los campos del subtopic
        update_data = subtopic.model_dump(exclude_unset=True)
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
