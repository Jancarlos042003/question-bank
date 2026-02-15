import logging

from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.course.repository import CourseRepository
from app.core.exceptions.technical import PersistenceError

logger = logging.getLogger(__name__)


class CourseService:
    def __init__(self, repository: CourseRepository):
        self.repository = repository

    def get_course(self, course_id: int):
        try:
            course = self.repository.get_course(course_id)
            return course
        except SQLAlchemyError as e:
            logger.error(
                f"Error al validar el curso con id {course_id} para crear tópico: {e}"
            )
            raise PersistenceError("Error al validar el curso en la base de datos")
