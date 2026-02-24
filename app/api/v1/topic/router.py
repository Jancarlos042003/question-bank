from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.v1.topic.schemas import (
    TopicCreate,
    TopicPublic,
    TopicPublicNoDescription,
    TopicUpdate,
)
from app.db.session import get_session
from app.helpers.build_paginated import build_paginated_response
from app.schemas.pagination import PaginationMeta
from app.schemas.response import ApiResponse
from app.repositories.course_repository import CourseRepository
from app.repositories.topic_repository import TopicRepository
from app.services.course_service import CourseService
from app.services.topic_service import TopicService

topic_router = APIRouter(tags=["Topic"])


# Inyección de Dependencia
def get_course_service(db: Annotated[Session, Depends(get_session)]):
    course_repository = CourseRepository(db)
    return CourseService(course_repository)


def get_topic_service(
        db: Annotated[Session, Depends(get_session)],
        course_service: Annotated[CourseService, Depends(get_course_service)],
):
    topic_repository = TopicRepository(db)

    return TopicService(topic_repository, course_service)


@topic_router.post(
    "",
    response_model=ApiResponse[TopicPublic],
    status_code=status.HTTP_201_CREATED,
    summary="Crea un nuevo tema",
)
def add_topic(
        service: Annotated[TopicService, Depends(get_topic_service)], topic: TopicCreate
):
    """Crea un nuevo tema con los datos proporcionados."""
    created_topic = service.create_topic(topic)
    return {"data": created_topic}


@topic_router.get(
    "",
    response_model=ApiResponse[list[TopicPublic], PaginationMeta],
    summary="Lista de temas",
)
def read_topics(
        service: Annotated[TopicService, Depends(get_topic_service)],
        page: Annotated[int, Query(ge=1, description="Número de página")] = 1,
        limit: Annotated[
            int, Query(ge=1, le=100, description="Cantidad de elementos por página")
        ] = 50,
):
    """Recupera una lista de temas con soporte de paginación."""
    items, total = service.get_topics(page, limit)
    return build_paginated_response(items=items, total=total, page=page, limit=limit)


@topic_router.get(
    "/{topic_id}",
    response_model=ApiResponse[TopicPublic | TopicPublicNoDescription],
    summary="Obtener un tema",
)
def read_topic(
        service: Annotated[TopicService, Depends(get_topic_service)],
        topic_id: Annotated[int, Path(description="ID del tema", ge=1)],
        include_description: Annotated[
            bool, Query(description="Incluir descripción del tema")
        ] = True,
):
    """Recupera los detalles de un tema específico utilizando su ID."""
    topic = service.get_topic(topic_id, include_description)
    return {"data": topic}


@topic_router.patch(
    "/{topic_id}", response_model=ApiResponse[TopicPublic], summary="Actualizar un tema"
)
def update_topic(
        service: Annotated[TopicService, Depends(get_topic_service)],
        topic_id: Annotated[int, Path(description="ID del tema", ge=1)],
        topic: TopicUpdate,
):
    """Actualiza la información de un tema existente."""
    updated_topic = service.update_topic(topic_id, topic)
    return {"data": updated_topic}


@topic_router.delete(
    "/{topic_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un tema"
)
def delete_topic(
        service: Annotated[TopicService, Depends(get_topic_service)],
        topic_id: Annotated[int, Path(description="ID del tema", ge=1)],
):
    """Elimina un tema del sistema."""
    return service.delete_topic(topic_id)
