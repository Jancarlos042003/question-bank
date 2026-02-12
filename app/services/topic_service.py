from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.course.repository import CourseRepository
from app.api.v1.topic.repository import TopicRepository
from app.api.v1.topic.schemas import (
    TopicCreate,
    TopicPublic,
    TopicPublicNoDescription,
    TopicUpdate,
)
from app.core.exceptions.domain import ResourceNotFoundException
from app.core.exceptions.technical import PersistenceError


class TopicService:
    def __init__(
        self, repository: TopicRepository, course_repository: CourseRepository
    ):
        self.repository = repository
        self.course_repository = course_repository

    def get_topic(self, topic_id: int, include_description: bool):
        topic = self.repository.get_topic(topic_id)

        if not topic:
            raise ResourceNotFoundException(
                message=f"Topic with id {topic_id} not found"
            )

        if include_description:
            # Valida y transforma el objeto topic en una instancia de TopicPublic
            return TopicPublic.model_validate(topic)

        # Se excluye description
        return TopicPublicNoDescription.model_validate(topic)

    def get_topics(self, page: int, limit: int):
        return self.repository.get_topics(page, limit)

    def create_topic(self, topic: TopicCreate):
        # Validar que el ID de curso (FK) exista
        course = self.course_repository.get_course(topic.course_id)

        if not course:
            raise ResourceNotFoundException(
                f"Course with id {topic.course_id} not found"
            )

        try:
            new_topic = self.repository.create_topic(topic)
        except SQLAlchemyError:
            raise PersistenceError("Error persisting topic")
        else:
            return new_topic

    def update_topic(self, topic_id: int, topic: TopicUpdate):
        # Validar que el ID de curso (FK) exista
        if topic.course_id is not None:
            course = self.course_repository.get_course(topic.course_id)

            if not course:
                raise ResourceNotFoundException(
                    f"Course with id {topic.course_id} not found"
                )

        updated_topic = self.repository.update_topic(topic_id, topic)

        if not updated_topic:
            raise ResourceNotFoundException(
                message=f"Topic with id {topic_id} not found"
            )

        return updated_topic

    def delete_topic(self, topic_id: int):
        topic = self.repository.delete_topic(topic_id)

        if not topic:
            raise ResourceNotFoundException(
                message=f"Topic with id {topic_id} not found"
            )

        return topic
