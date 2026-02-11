from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.topic.schemas import TopicCreate, TopicUpdate
from app.models.topic import Topic


class TopicRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_topic(self, topic_id: int):
        stmt = select(Topic).where(Topic.id == topic_id)
        return self.db.scalar(stmt)

    def get_topics(self, skip: int = 0, limit: int = 100):
        stmt = select(Topic).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def create_topic(self, topic: TopicCreate):
        db_topic = Topic(**topic.model_dump())
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

    def update_topic(self, topic_id: int, topic: TopicUpdate):
        stmt = select(Topic).where(Topic.id == topic_id)
        db_topic = self.db.scalar(stmt)

        if not db_topic:
            return None

        update_data = topic.model_dump(exclude_unset=True)
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
