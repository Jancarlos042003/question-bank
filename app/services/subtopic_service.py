import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.subtopic.repository import SubtopicRepository
from app.api.v1.subtopic.schemas import SubtopicCreate, SubtopicUpdate
from app.api.v1.topic.repository import TopicRepository
from app.core.exceptions.domain import ResourceNotFoundException
from app.core.exceptions.technical import PersistenceError, RetrievalError, DeleteError

logger = logging.getLogger(__name__)


class SubtopicService:
    def __init__(
            self, repository: SubtopicRepository, topic_repository: TopicRepository
    ):
        self.repository = repository
        self.topic_repository = topic_repository

    def get_subtopic(self, subtopic_id: int):
        try:
            subtopic = self.repository.get_subtopic(subtopic_id)
        except SQLAlchemyError as e:
            logger.exception(f"Error al obtener el subtema con ID {subtopic_id}")
            raise RetrievalError(
                f"Error al obtener el subtema con ID {subtopic_id}"
            ) from e

        if not subtopic:
            raise ResourceNotFoundException(
                message=f"Subtema con ID {subtopic_id} no encontrado."
            )
        return subtopic

    def get_subtopics(self, page: int, limit: int):
        try:
            return self.repository.get_subtopics(page, limit)
        except SQLAlchemyError as e:
            logger.exception(f"Error al listar subtemas (page={page}, limit={limit})")
            raise RetrievalError(
                f"Error al listar subtemas (page={page}, limit={limit})"
            ) from e

    def create_subtopic(self, subtopic: SubtopicCreate):
        # Validar que el ID de topic (FK) exista
        if subtopic.topic_id is not None:
            topic = self.topic_repository.get_topic(subtopic.topic_id)

            if not topic:
                raise ResourceNotFoundException(
                    message=f"Topic with id {subtopic.topic_id} not found"
                )

        try:
            new_subtopic = self.repository.create_subtopic(subtopic)
        except IntegrityError as e:
            logger.exception("IntegrityError al crear subtema")
            raise PersistenceError("Error al persistir el subtema") from e
        except SQLAlchemyError as e:
            logger.exception("Error al persistir el subtema")
            raise PersistenceError("Error al persistir el subtema") from e
        else:
            return new_subtopic

    def update_subtopic(self, subtopic_id: int, subtopic: SubtopicUpdate):
        # Validar que el ID de topic (FK) exista
        if subtopic.topic_id is not None:
            topic = self.topic_repository.get_topic(subtopic.topic_id)

            if not topic:
                raise ResourceNotFoundException(
                    message=f"Tema con ID {subtopic.topic_id} no encontrado"
                )

        try:
            updated_subtopic = self.repository.update_subtopic(subtopic_id, subtopic)
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar subtema")
            raise PersistenceError("Error al actualizar el subtema") from e
        except SQLAlchemyError as e:
            logger.exception("Error al actualizar el subtema")
            raise PersistenceError("Error al actualizar el subtema") from e

        if not updated_subtopic:
            raise ResourceNotFoundException(
                f"Subtema con ID {subtopic_id} no encontrado"
            )

        return updated_subtopic

    def delete_subtopic(self, subtopic_id: int):
        try:
            subtopic = self.repository.delete_subtopic(subtopic_id)
        except SQLAlchemyError as e:
            logger.exception(f"Error al eliminar el subtema con ID {subtopic_id}")
            raise DeleteError(
                f"Error al eliminar el subtema con ID {subtopic_id}"
            ) from e

        if not subtopic:
            raise ResourceNotFoundException(
                f"Subtema con ID {subtopic_id} no encontrado"
            )

        return subtopic
