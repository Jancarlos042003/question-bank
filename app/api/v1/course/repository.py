from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.course.schemas import CourseCreate, CourseUpdate
from app.models.course import Course


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_course(self, course_id: int):
        stmt = select(Course).where(Course.id == course_id)
        return self.db.scalar(stmt)

    def get_courses(self, skip: int = 0, limit: int = 100):
        stmt = select(Course).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def create_course(self, course: CourseCreate):
        db_course = Course(**course.model_dump())
        try:
            self.db.add(db_course)
            self.db.commit()
            self.db.refresh(db_course)
            return db_course
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_course(self, course_id: int, course: CourseUpdate):
        stmt = select(Course).where(Course.id == course_id)
        db_course = self.db.scalar(stmt)

        if not db_course:
            return None

        update_data = course.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_course, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_course)
            return db_course
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_course(self, course_id: int):
        stmt = select(Course).where(Course.id == course_id)
        db_course = self.db.scalar(stmt)

        if not db_course:
            return None

        try:
            self.db.delete(db_course)
            self.db.commit()
            return db_course
        except SQLAlchemyError:
            self.db.rollback()
            raise
