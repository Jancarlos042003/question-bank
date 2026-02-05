from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.area import Area


def get_areas(db: Session, ids: List[int]):
    stmt = select(Area).where(Area.id.in_(ids))
    return db.scalars(stmt).all()
