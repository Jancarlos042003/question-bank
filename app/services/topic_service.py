from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.topic.repository import TopicRepository
from app.api.v1.topic.schemas import TopicCreate, TopicUpdate
from app.core.exceptions.domain import ResourceNotFoundException
from app.core.exceptions.technical import PersistenceError


class TopicService:
    def __init__(self, repository: TopicRepository):
        self.repository = repository

    def get_topic(self, topic_id: int):
        topic = self.repository.get_topic(topic_id)

        if not topic:
            raise ResourceNotFoundException(message="Topic not found")

        return topic

    def get_topics(self, skip: int = 0, limit: int = 100):
        return self.repository.get_topics(skip, limit)

    def create_topic(self, topic: TopicCreate):
        try:
            new_topic = self.repository.create_topic(topic)
        except SQLAlchemyError:
            raise PersistenceError("Error persisting topic")
        else:
            return new_topic

    def update_topic(self, topic_id: int, topic: TopicUpdate):
        updated_topic = self.repository.update_topic(topic_id, topic)

        if not updated_topic:
            raise ResourceNotFoundException(message="Topic not found")

        return updated_topic

    def delete_topic(self, topic_id: int):
        topic = self.repository.delete_topic(topic_id)

        if not topic:
            raise ResourceNotFoundException(message="Topic not found")

        return topic
