from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.v1.subtopic.repository import SubtopicRepository
from app.api.v1.subtopic.schemas import (
    SubtopicCreate,
    SubtopicPaginatedResponse,
    SubtopicPublic,
    SubtopicUpdate,
)
from app.db.session import get_session
from app.services.subtopic_service import SubtopicService

subtopic_router = APIRouter(tags=["Subtopic"])


def get_subtopic_service(db: Annotated[Session, Depends(get_session)]):
    repository = SubtopicRepository(db)
    service = SubtopicService(repository)
    return service


@subtopic_router.post(
    "",
    response_model=SubtopicPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un nuevo subtema",
)
def add_subtopic(
    service: Annotated[SubtopicService, Depends(get_subtopic_service)],
    subtopic: SubtopicCreate,
):
    """Crea un nuevo subtema con los datos proporcionados."""
    return service.create_subtopic(subtopic)


@subtopic_router.get(
    "",
    response_model=SubtopicPaginatedResponse,
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
    return service.get_subtopics(page, limit)


@subtopic_router.get(
    "/{subtopic_id}",
    response_model=SubtopicPublic,
    summary="Obtener un subtema por ID",
)
def read_subtopic(
    service: Annotated[SubtopicService, Depends(get_subtopic_service)],
    subtopic_id: Annotated[int, Path(ge=1, description="ID del subtema")],
):
    """
    Recupera los detalles de un subtema específico utilizando su identificador único.
    """
    return service.get_subtopic(subtopic_id)


@subtopic_router.patch(
    "/{subtopic_id}",
    response_model=SubtopicPublic,
    summary="Actualizar un subtema",
)
def update_subtopic(
    service: Annotated[SubtopicService, Depends(get_subtopic_service)],
    subtopic_id: Annotated[int, Path(ge=1, description="ID del subtema")],
    subtopic: SubtopicUpdate,
):
    """Actualiza la información de un subtema existente."""
    return service.update_subtopic(subtopic_id, subtopic)


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
