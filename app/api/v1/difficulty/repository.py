from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.difficulty.schemas import DifficultyCreate
from app.models.difficulty import Difficulty


def create_difficulty(db: Session, difficulty: DifficultyCreate):
    db_difficulty = Difficulty(**difficulty.model_dump())
    db.add(db_difficulty)
    db.commit()
    db.refresh(db_difficulty)
    return db_difficulty

def get_difficulty_by_id(db: Session, id: int):
    stmt = select(Difficulty).where(Difficulty.id == id)
    return db.scalar(stmt)
