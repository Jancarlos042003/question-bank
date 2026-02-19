import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.domain import ResourceNotFoundException
from app.core.exceptions.technical import RetrievalError
from app.repositories.course_repository import CourseRepository

logger = logging.getLogger(__name__)


class CourseService:
    def __init__(self, repository: CourseRepository):
        self.repository = repository

    def get_course(self, course_id: int):
        try:
            course = self.repository.get_course(course_id)

            if not course:
                raise ResourceNotFoundException(
                    f"No se encontró el curso con id {course_id}"
                )

            return course
        except SQLAlchemyError as e:
            logger.error(
                f"Error al validar el curso con id {course_id} para crear tópico: {e}"
            )
            raise RetrievalError("Error al validar el curso en la base de datos")
