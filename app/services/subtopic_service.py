from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.subtopic.repository import SubtopicRepository
from app.api.v1.subtopic.schemas import SubtopicCreate, SubtopicUpdate
from app.api.v1.topic.repository import TopicRepository
from app.core.exceptions.domain import ResourceNotFoundException
from app.core.exceptions.technical import PersistenceError


class SubtopicService:
    def __init__(
        self, repository: SubtopicRepository, topic_repository: TopicRepository
    ):
        self.repository = repository
        self.topic_repository = topic_repository

    def get_subtopic(self, subtopic_id: int):
        subtopic = self.repository.get_subtopic(subtopic_id)
        if not subtopic:
            raise ResourceNotFoundException(
                message=f"Subtopic with id {subtopic_id} not found"
            )
        return subtopic_id

    def get_subtopics(self, page: int, limit: int):
        return self.repository.get_subtopics(page, limit)

    def create_subtopic(self, subtopic: SubtopicCreate):
        try:
            new_subtopic = self.repository.create_subtopic(subtopic)
        except IntegrityError:
            raise ResourceNotFoundException(
                message=f"Topic with id {subtopic.topic_id} not found"
            )
        except SQLAlchemyError:
            raise PersistenceError("Error persisting subtopic")
        else:
            return new_subtopic

    def update_subtopic(self, subtopic_id: int, subtopic: SubtopicUpdate):
        # Validar que el ID de topic (FK) exista
        if subtopic.topic_id is not None:
            topic = self.topic_repository.get_topic(subtopic.topic_id)

            if not topic:
                raise ResourceNotFoundException(
                    message=f"Topic with id {subtopic.topic_id} not found"
                )

        try:
            updated_subtopic = self.repository.update_subtopic(subtopic_id, subtopic)
        except SQLAlchemyError:
            raise PersistenceError("Error persisting subtopic")

        if not updated_subtopic:
            raise ResourceNotFoundException(
                message=f"Subtopic with id {subtopic_id} not found"
            )

        return updated_subtopic

    def delete_subtopic(self, subtopic_id: int):
        subtopic = self.repository.delete_subtopic(subtopic_id)

        if not subtopic:
            raise ResourceNotFoundException(
                message=f"Subtopic with id {subtopic_id} not found"
            )

        return subtopic
