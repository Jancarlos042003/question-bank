from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.area import Area


class AreaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_areas(self, ids: List[int]):
        try:
            stmt = select(Area).where(Area.id.in_(ids))
            areas = self.db.scalars(stmt).all()
        except SQLAlchemyError:
            raise
        else:
            return areas
