from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.subtopic import repository
from app.api.v1.subtopic.schemas import SubtopicCreate, SubtopicPublic, SubtopicUpdate
from app.db.session import get_session

subtopic_router = APIRouter(tags=["Subtopic"])


@subtopic_router.post(
    "", response_model=SubtopicPublic, status_code=status.HTTP_201_CREATED
)
def add_subtopic(
    db: Annotated[Session, Depends(get_session)], subtopic: SubtopicCreate
):
    return repository.create_subtopic(db, subtopic)


@subtopic_router.get("", response_model=list[SubtopicPublic])
def read_subtopics(
    db: Annotated[Session, Depends(get_session)], skip: int = 0, limit: int = 100
):
    return repository.get_subtopics(db, skip, limit)


@subtopic_router.get("/{subtopic_id}", response_model=SubtopicPublic)
def read_subtopic(db: Annotated[Session, Depends(get_session)], subtopic_id: int):
    db_subtopic = repository.get_subtopic(db, subtopic_id)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return db_subtopic


@subtopic_router.patch("/{subtopic_id}", response_model=SubtopicPublic)
def update_subtopic(
    db: Annotated[Session, Depends(get_session)],
    subtopic_id: int,
    subtopic: SubtopicUpdate,
):
    db_subtopic = repository.update_subtopic(db, subtopic_id, subtopic)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return db_subtopic


@subtopic_router.delete("/{subtopic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subtopic(db: Annotated[Session, Depends(get_session)], subtopic_id: int):
    db_subtopic = repository.delete_subtopic(db, subtopic_id)
    if db_subtopic is None:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return
