from collections.abc import Mapping

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.cache import get_cached_count, set_cached_count
from app.models.institution import Institution


class InstitutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_institution(self, institution_id: int):
        stmt = select(Institution).where(Institution.id == institution_id)
        return self.db.scalar(stmt)

    def get_institutions(self, page: int, limit: int):
        offset = (page - 1) * limit

        stmt = select(Institution).offset(offset).limit(limit)
        items = list(self.db.scalars(stmt).all())

        # Intentar obtener del caché
        total = get_cached_count(name="institutions:total_count")

        if total is None:
            total = self.db.scalar(select(func.count()).select_from(Institution))
            # Guardar en caché por 5 minutos
            set_cached_count(name="institutions:total_count", value=total, ttl=300)

        return items, total

    def get_institutions_by_ids(self, ids: list[int]):
        stmt = select(Institution).where(Institution.id.in_(ids))
        return list(self.db.scalars(stmt).all())

    def create_institution(self, institution_data: Mapping[str, object]):
        db_institution = Institution(**institution_data)

        try:
            self.db.add(db_institution)
            self.db.commit()
            self.db.refresh(db_institution)
            return db_institution
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_institution(
            self, institution_id: int, update_data: Mapping[str, object]
    ):
        stmt = select(Institution).where(Institution.id == institution_id)
        db_institution = self.db.scalar(stmt)

        if not db_institution:
            return None

        for key, value in update_data.items():
            setattr(db_institution, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_institution)
            return db_institution
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_institution(self, institution_id: int):
        stmt = select(Institution).where(Institution.id == institution_id)
        db_institution = self.db.scalar(stmt)

        if not db_institution:
            return None

        try:
            self.db.delete(db_institution)
            self.db.commit()
            return db_institution
        except SQLAlchemyError:
            self.db.rollback()
            raise
