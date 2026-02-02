from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.subtopic.schemas import SubtopicCreate, SubtopicUpdate
from app.models.subtopic import Subtopic


def get_subtopic(db: Session, subtopic_id: int):
    stmt = select(Subtopic).where(Subtopic.id == subtopic_id)
    return db.scalar(stmt)


def get_subtopics(db: Session, skip: int = 0, limit: int = 100):
    stmt = select(Subtopic).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def create_subtopic(db: Session, subtopic: SubtopicCreate):
    db_subtopic = Subtopic(**subtopic.model_dump())
    db.add(db_subtopic)
    db.commit()
    db.refresh(db_subtopic)
    return db_subtopic


def update_subtopic(
    db: Session, subtopic_id: int, subtopic: SubtopicUpdate
):
    stmt = select(Subtopic).where(Subtopic.id == subtopic_id)
    db_subtopic = db.scalar(stmt)
    if db_subtopic:
        update_data = subtopic.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_subtopic, key, value)
        db.commit()
        db.refresh(db_subtopic)
    return db_subtopic


def delete_subtopic(db: Session, subtopic_id: int):
    stmt = select(Subtopic).where(Subtopic.id == subtopic_id)
    db_subtopic = db.scalar(stmt)
    if db_subtopic:
        db.delete(db_subtopic)
        db.commit()
    return db_subtopic
