from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.topic.repository import TopicRepository
from app.api.v1.topic.schemas import TopicCreate, TopicResponse, TopicUpdate
from app.db.session import get_session
from app.services.topic_service import TopicService

topic_router = APIRouter(tags=["Topic"])


def get_topic_service(db: Annotated[Session, Depends(get_session)]):
    repository = TopicRepository(db)
    return TopicService(repository)


@topic_router.post(
    "", response_model=TopicResponse, status_code=status.HTTP_201_CREATED
)
def add_topic(
    service: Annotated[TopicService, Depends(get_topic_service)], topic: TopicCreate
):
    return service.create_topic(topic)


@topic_router.get("", response_model=list[TopicResponse])
def read_topics(
    service: Annotated[TopicService, Depends(get_topic_service)],
    skip: int = 0,
    limit: int = 100,
):
    return service.get_topics(skip, limit)


@topic_router.get("/{topic_id}", response_model=TopicResponse)
def read_topic(
    service: Annotated[TopicService, Depends(get_topic_service)], topic_id: int
):
    return service.get_topic(topic_id)


@topic_router.patch("/{topic_id}", response_model=TopicResponse)
def update_topic(
    service: Annotated[TopicService, Depends(get_topic_service)],
    topic_id: int,
    topic: TopicUpdate,
):
    return service.update_topic(topic_id, topic)


@topic_router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    service: Annotated[TopicService, Depends(get_topic_service)], topic_id: int
):
    return service.delete_topic(topic_id)
