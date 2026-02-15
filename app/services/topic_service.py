import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.topic.repository import TopicRepository
from app.api.v1.topic.schemas import (
    TopicCreate,
    TopicPublic,
    TopicPublicNoDescription,
    TopicUpdate,
)
from app.core.exceptions.domain import ResourceNotFoundException
from app.core.exceptions.technical import DeleteError, PersistenceError
from app.services.course_service import CourseService

logger = logging.getLogger(__name__)


class TopicService:
    def __init__(self, repository: TopicRepository, course_service: CourseService):
        self.repository = repository
        self.course_service = course_service

    def get_topic(self, topic_id: int, include_description: bool):
        try:
            topic = self.repository.get_topic(topic_id)
        except SQLAlchemyError as e:
            logger.error(
                f"Error al obtener el tópico con id {topic_id} desde la base de datos: {e}"
            )
            raise PersistenceError("Error al obtener el tópico desde la base de datos")

        if not topic:
            raise ResourceNotFoundException(
                message=f"No se encontró el tópico con id {topic_id}"
            )

        if include_description:
            # Valida y transforma el objeto topic en una instancia de TopicPublic
            return TopicPublic.model_validate(topic)

        # Se excluye description
        return TopicPublicNoDescription.model_validate(topic)

    def get_topics(self, page: int, limit: int):
        try:
            return self.repository.get_topics(page, limit)
        except SQLAlchemyError as e:
            logger.error(
                f"Error al listar tópicos desde la base de datos (page={page}, limit={limit}): {e}"
            )
            raise PersistenceError("Error al listar los tópicos desde la base de datos")

    def create_topic(self, topic: TopicCreate):
        # Validar que el ID de curso (FK) exista
        course = self.course_service.get_course(topic.course_id)

        if not course:
            raise ResourceNotFoundException(
                f"No se encontró el curso con id {topic.course_id}"
            )

        try:
            new_topic = self.repository.create_topic(topic)
        except IntegrityError as e:
            logger.error(
                f"Error al crear el tema (course_id={topic.course_id,}): {e}",
            )
            raise PersistenceError("Error al crear el tema en la base de datos")
        except SQLAlchemyError as e:
            logger.error(f"Error al crear el tópico en la base de datos: {e}")
            raise PersistenceError("Error al crear el tópico en la base de datos")
        else:
            return new_topic

    def update_topic(self, topic_id: int, topic: TopicUpdate):
        # Validar que el ID de curso (FK) exista
        course = self.course_service.get_course(topic.course_id)

        if not course:
            raise ResourceNotFoundException(
                f"No se encontró el curso con id {topic.course_id}"
            )

        try:
            updated_topic = self.repository.update_topic(topic_id, topic)
        except IntegrityError as e:
            logger.error(f"Error al actualizar el tema con id {topic_id}: {e}")
            raise PersistenceError("Error al actualizar el tema en la base de datos")
        except SQLAlchemyError as e:
            logger.error(
                f"Error al actualizar el tema con id {topic_id} en la base de datos: {e}"
            )
            raise PersistenceError("Error al actualizar el tema en la base de datos")

        if not updated_topic:
            raise ResourceNotFoundException(
                message=f"No se encontró el tema con id {topic_id}"
            )

        return updated_topic

    def delete_topic(self, topic_id: int):
        try:
            topic = self.repository.delete_topic(topic_id)
        except SQLAlchemyError as e:
            logger.error(
                "Error al eliminar el tema con id %s en la base de datos: %s",
                topic_id,
                e,
            )
            raise DeleteError(f"Error al eliminar el tema con id {topic_id}")

        if not topic:
            raise ResourceNotFoundException(
                message=f"No se encontró el tema con id {topic_id}"
            )

        return topic
