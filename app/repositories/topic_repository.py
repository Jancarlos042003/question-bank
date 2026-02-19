import math
from collections.abc import Mapping

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.topic import Topic
from app.repositories.pagination import PaginatedResult


class TopicRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_topic(self, topic_id: int):
        stmt = select(Topic).where(Topic.id == topic_id)
        return self.db.scalar(stmt)

    def get_topics(self, page: int, limit: int) -> PaginatedResult[Topic]:
        offset = (page - 1) * limit

        stmt = select(Topic).offset(offset).limit(limit)
        items = list(self.db.scalars(stmt).all())

        total_count = self.db.scalar(select(func.count()).select_from(Topic))

        total_pages = max(1, math.ceil(total_count / limit))

        has_prev = page > 1
        has_next = page < total_pages

        return PaginatedResult(
            total_count=total_count,
            total_pages=total_pages,
            current_page=page,
            items_count=len(items),
            has_prev=has_prev,
            has_next=has_next,
            items=items,
        )

    def create_topic(self, topic_data: Mapping[str, object]):
        db_topic = Topic(**topic_data)
        try:
            self.db.add(db_topic)
            self.db.commit()
            self.db.refresh(db_topic)
            return db_topic
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_topic(self, topic_id: int, update_data: Mapping[str, object]):
        stmt = select(Topic).where(Topic.id == topic_id)
        db_topic = self.db.scalar(stmt)

        if not db_topic:
            return None

        for key, value in update_data.items():
            setattr(db_topic, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_topic)
            return db_topic
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_topic(self, topic_id: int):
        stmt = select(Topic).where(Topic.id == topic_id)
        db_topic = self.db.scalar(stmt)

        if not db_topic:
            return None

        try:
            self.db.delete(db_topic)
            self.db.commit()
            return db_topic
        except SQLAlchemyError:
            self.db.rollback()
            raise
