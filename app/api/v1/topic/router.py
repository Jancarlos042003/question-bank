from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.v1.topic.schemas import (
    TopicCreate,
    TopicPaginatedResponse,
    TopicPublic,
    TopicPublicNoDescription,
    TopicUpdate,
)
from app.db.session import get_session
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
    response_model=TopicPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un nuevo tema",
)
def add_topic(
        service: Annotated[TopicService, Depends(get_topic_service)], topic: TopicCreate
):
    """Crea un nuevo tema con los datos proporcionados."""
    return service.create_topic(topic)


@topic_router.get("", response_model=TopicPaginatedResponse, summary="Lista de temas")
def read_topics(
        service: Annotated[TopicService, Depends(get_topic_service)],
        page: Annotated[int, Query(ge=1, description="Número de página")] = 1,
        limit: Annotated[
            int, Query(ge=1, le=100, description="Cantidad de elementos por página")
        ] = 50,
):
    """Recupera una lista de temas con soporte de paginación."""
    return service.get_topics(page, limit)


@topic_router.get(
    "/{topic_id}",
    response_model=TopicPublic | TopicPublicNoDescription,
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
    return service.get_topic(topic_id, include_description)


@topic_router.patch(
    "/{topic_id}", response_model=TopicPublic, summary="Actualizar un tema"
)
def update_topic(
        service: Annotated[TopicService, Depends(get_topic_service)],
        topic_id: Annotated[int, Path(description="ID del tema", ge=1)],
        topic: TopicUpdate,
):
    """Actualiza la información de un tema existente."""
    return service.update_topic(topic_id, topic)


@topic_router.delete(
    "/{topic_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un tema"
)
def delete_topic(
        service: Annotated[TopicService, Depends(get_topic_service)],
        topic_id: Annotated[int, Path(description="ID del tema", ge=1)],
):
    """Elimina un tema del sistema."""
    return service.delete_topic(topic_id)
