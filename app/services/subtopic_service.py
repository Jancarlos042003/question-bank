import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.subtopic.schemas import (
    SubtopicCreate,
    SubtopicPaginatedResponse,
    SubtopicPublic,
    SubtopicUpdate,
)
from app.core.exceptions.domain import ResourceNotFoundException
from app.core.exceptions.technical import PersistenceError, RetrievalError, DeleteError
from app.services.topic_service import TopicService
from app.repositories.subtopic_repository import SubtopicRepository

logger = logging.getLogger(__name__)


class SubtopicService:
    def __init__(self, repository: SubtopicRepository, topic_service: TopicService):
        self.repository = repository
        self.topic_service = topic_service

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
            subtopics_page = self.repository.get_subtopics(page, limit)
        except SQLAlchemyError as e:
            logger.exception(f"Error al listar subtemas (page={page}, limit={limit})")
            raise RetrievalError(
                f"Error al listar subtemas (page={page}, limit={limit})"
            ) from e

        items = [
            SubtopicPublic.model_validate(subtopic) for subtopic in subtopics_page.items
        ]
        return SubtopicPaginatedResponse(
            total_count=subtopics_page.total_count,
            total_pages=subtopics_page.total_pages,
            current_page=subtopics_page.current_page,
            items_count=subtopics_page.items_count,
            has_prev=subtopics_page.has_prev,
            has_next=subtopics_page.has_next,
            items=items,
        )

    def create_subtopic(self, subtopic: SubtopicCreate):
        # Validar que el ID de topic (FK) exista
        self.topic_service.get_topic(
            topic_id=subtopic.topic_id, include_description=False
        )

        try:
            new_subtopic = self.repository.create_subtopic(subtopic.model_dump())
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
        self.topic_service.get_topic(
            topic_id=subtopic.topic_id, include_description=False
        )

        try:
            updated_subtopic = self.repository.update_subtopic(
                subtopic_id, subtopic.model_dump(exclude_unset=True)
            )
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
