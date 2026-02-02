from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.topic.schemas import TopicCreate, TopicUpdate
from app.models.topic import Topic


def get_topic(db: Session, topic_id: int):
    stmt = select(Topic).where(Topic.id == topic_id)
    return db.scalar(stmt)


def get_topics(db: Session, skip: int = 0, limit: int = 100):
    stmt = select(Topic).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def create_topic(db: Session, topic: TopicCreate):
    db_topic = Topic(**topic.model_dump())

    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)

    return db_topic


def update_topic(db: Session, topic_id: int, topic: TopicUpdate):
    stmt = select(Topic).where(Topic.id == topic_id)
    db_topic = db.scalar(stmt)

    if db_topic:
        update_data = topic.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_topic, key, value)
        db.commit()
        db.refresh(db_topic)

    return db_topic


def delete_topic(db: Session, topic_id: int):
    stmt = select(Topic).where(Topic.id == topic_id)
    db_topic = db.scalar(stmt)

    if db_topic:
        db.delete(db_topic)
        db.commit()
    return db_topic
