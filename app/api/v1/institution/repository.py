import math

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.institution.schemas import (
    InstitutionCreate,
    InstitutionPaginatedResponse,
    InstitutionUpdate,
)
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

        total_count = self.db.scalar(select(func.count()).select_from(Institution))
        total_pages = max(1, math.ceil(total_count / limit))

        has_prev = page > 1
        has_next = page < total_pages

        return InstitutionPaginatedResponse(
            total_count=total_count,
            total_pages=total_pages,
            current_page=page,
            items_count=len(items),
            has_prev=has_prev,
            has_next=has_next,
            items=items,
        )

    def get_institutions_by_ids(self, ids: list[int]):
        stmt = select(Institution).where(Institution.id.in_(ids))
        return list(self.db.scalars(stmt).all())

    def create_institution(self, institution: InstitutionCreate):
        db_institution = Institution(**institution.model_dump())

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

    def update_institution(self, institution_id: int, institution: InstitutionUpdate):
        stmt = select(Institution).where(Institution.id == institution_id)
        db_institution = self.db.scalar(stmt)

        if not db_institution:
            return None

        update_data = institution.model_dump(exclude_unset=True)
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
