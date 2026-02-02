from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.topic import repository
from app.api.v1.topic.schemas import TopicCreate, TopicRead, TopicUpdate
from app.db.session import get_session

topic_router = APIRouter(tags=["Topic"])


@topic_router.post("", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
def add_topic(db: Annotated[Session, Depends(get_session)], topic: TopicCreate):
    return repository.create_topic(db, topic)


@topic_router.get("", response_model=list[TopicRead])
def read_topics(
    db: Annotated[Session, Depends(get_session)], skip: int = 0, limit: int = 100
):
    return repository.get_topics(db, skip, limit)


@topic_router.get("/{topic_id}", response_model=TopicRead)
def read_topic(db: Annotated[Session, Depends(get_session)], topic_id: int):
    db_topic = repository.get_topic(db, topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Tema de encontrado")
    return db_topic


@topic_router.patch("/{topic_id}", response_model=TopicRead)
def update_topic(
    db: Annotated[Session, Depends(get_session)], topic_id: int, topic: TopicUpdate
):
    db_topic = repository.update_topic(db, topic_id, topic)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Tema de encontrado")
    return db_topic


@topic_router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(db: Annotated[Session, Depends(get_session)], topic_id: int):
    db_topic = repository.delete_topic(db, topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Tema de encontrado")
