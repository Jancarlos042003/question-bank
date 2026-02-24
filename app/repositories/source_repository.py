from collections.abc import Mapping

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.cache import get_cached_count, set_cached_count
from app.models.source import Source


class SourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_source(self, source_id: int):
        stmt = select(Source).where(Source.id == source_id)
        return self.db.scalar(stmt)

    def get_sources(self, page: int, limit: int):
        offset = (page - 1) * limit

        stmt = select(Source).offset(offset).limit(limit)
        items = list(self.db.scalars(stmt).all())

        total = get_cached_count("sources:total_count")
        if total is None:
            total = self.db.scalar(select(func.count()).select_from(Source))
            set_cached_count(name="sources:total_count", value=total, ttl=300)

        return items

    def get_sources_by_ids(self, ids: list[int]):
        stmt = select(Source).where(Source.id.in_(ids))
        return list(self.db.scalars(stmt).all())

    def create_source(self, source_data: Mapping[str, object]):
        db_source = Source(**source_data)

        try:
            self.db.add(db_source)
            self.db.commit()
            self.db.refresh(db_source)
            return db_source
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_source(self, source_id: int, update_data: Mapping[str, object]):
        stmt = select(Source).where(Source.id == source_id)
        db_source = self.db.scalar(stmt)

        if not db_source:
            return None

        for key, value in update_data.items():
            setattr(db_source, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_source)
            return db_source
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_source(self, source_id: int):
        stmt = select(Source).where(Source.id == source_id)
        db_source = self.db.scalar(stmt)

        if not db_source:
            return None

        try:
            self.db.delete(db_source)
            self.db.commit()
            return db_source
        except SQLAlchemyError:
            self.db.rollback()
            raise
