from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.v1.subtopic.schemas import (
    SubtopicCreate,
    SubtopicPublic,
    SubtopicUpdate,
)
from app.db.session import get_session
from app.helpers.build_paginated import build_paginated_response
from app.schemas.pagination import PaginationMeta
from app.schemas.response import ApiResponse
from app.repositories.subtopic_repository import SubtopicRepository
from app.repositories.topic_repository import TopicRepository
from app.services.subtopic_service import SubtopicService
from app.services.topic_service import TopicService

subtopic_router = APIRouter(tags=["Subtopic"])


# Inyección de Dependencia
def get_topic_service(db: Annotated[Session, Depends(get_session)]):
    topic_repository = TopicRepository(db)
    return TopicService(topic_repository)


def get_subtopic_service(
        db: Annotated[Session, Depends(get_session)],
        topic_service: Annotated[TopicService, Depends(get_topic_service)],
):
    subtopic_repository = SubtopicRepository(db)
    return SubtopicService(subtopic_repository, topic_service)


@subtopic_router.post(
    "",
    response_model=ApiResponse[SubtopicPublic],
    status_code=status.HTTP_201_CREATED,
    summary="Crea un nuevo subtema",
)
def add_subtopic(
        service: Annotated[SubtopicService, Depends(get_subtopic_service)],
        subtopic: SubtopicCreate,
):
    """Crea un nuevo subtema con los datos proporcionados."""
    created_subtopic = service.create_subtopic(subtopic)
    return {"data": created_subtopic}


@subtopic_router.get(
    "",
    response_model=ApiResponse[list[SubtopicPublic], PaginationMeta],
    summary="Lista de subtemas",
)
def read_subtopics(
        service: Annotated[SubtopicService, Depends(get_subtopic_service)],
        page: Annotated[int, Query(ge=1, description="Número de página")] = 1,
        limit: Annotated[
            int, Query(ge=1, le=100, description="Cantidad de elementos por página")
        ] = 100,
):
    """Recupera una lista de subtemas con soporte de paginación."""
    items, total = service.get_subtopics(page, limit)
    return build_paginated_response(items=items, total=total, page=page, limit=limit)


@subtopic_router.get(
    "/{subtopic_id}",
    response_model=ApiResponse[SubtopicPublic],
    summary="Obtener un subtema por ID",
)
def read_subtopic(
        service: Annotated[SubtopicService, Depends(get_subtopic_service)],
        subtopic_id: Annotated[int, Path(ge=1, description="ID del subtema")],
):
    """
    Recupera los detalles de un subtema específico utilizando su identificador único.
    """
    subtopic = service.get_subtopic(subtopic_id)
    return {"data": subtopic}


@subtopic_router.patch(
    "/{subtopic_id}",
    response_model=ApiResponse[SubtopicPublic],
    summary="Actualizar un subtema",
)
def update_subtopic(
        service: Annotated[SubtopicService, Depends(get_subtopic_service)],
        subtopic_id: Annotated[int, Path(ge=1, description="ID del subtema")],
        subtopic: SubtopicUpdate,
):
    """Actualiza la información de un subtema existente."""
    updated_subtopic = service.update_subtopic(subtopic_id, subtopic)
    return {"data": updated_subtopic}


@subtopic_router.delete(
    "/{subtopic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un subtema",
)
def delete_subtopic(
        service: Annotated[SubtopicService, Depends(get_subtopic_service)],
        subtopic_id: Annotated[int, Path(ge=1, description="ID del subtema")],
):
    """Elimina un subtema del sistema."""
    return service.delete_subtopic(subtopic_id)
