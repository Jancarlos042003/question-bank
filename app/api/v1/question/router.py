from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.v1.area.repository import AreaRepository
from app.api.v1.question.repository import QuestionRepository
from app.api.v1.question.schemas import (
    QuestionCreateInput,
    QuestionPaginatedResponse,
    QuestionStudyResponse,
)
from app.core.config import settings
from app.db.session import get_session
from app.infrastructure.gcp.storage_adapter import GCPStorageAdapter
from app.ports.storage_port import StoragePort
from app.services.area_service import AreaService
from app.services.image_service import ImageService
from app.services.question_service import QuestionService

question_router = APIRouter(tags=["Question"])


# Dependency injection
def get_area_service(db: Annotated[Session, Depends(get_session)]):
    area_repository = AreaRepository(db)
    return AreaService(area_repository)


def get_gcp_storage():
    return GCPStorageAdapter()


def get_image_service(storage: Annotated[StoragePort, Depends(get_gcp_storage)]):
    return ImageService(storage, settings.CONTAINER_NAME)


def get_question_service(
        db: Annotated[Session, Depends(get_session)],
        area_service: Annotated[AreaService, Depends(get_area_service)],
        image_service: Annotated[ImageService, Depends(get_image_service)],
) -> QuestionService:
    question_repository = QuestionRepository(db)

    return QuestionService(question_repository, area_service, image_service)


@question_router.post(
    "", response_model=QuestionStudyResponse, status_code=status.HTTP_201_CREATED
)
async def add_question(
        db: Annotated[Session, Depends(get_session)],
        service: Annotated[QuestionService, Depends(get_question_service)],
        question: QuestionCreateInput,
):
    """Endpoint para crear una nueva pregunta."""

    return await service.create_question(
        question=question,
    )


@question_router.get(
    "",
    response_model=QuestionPaginatedResponse,
    summary="Listar preguntas",
)
def get_questions(
        db: Annotated[Session, Depends(get_session)],
        service: Annotated[QuestionService, Depends(get_question_service)],
        page: Annotated[int, Query(ge=1, description="Página actual")] = 1,
        limit: Annotated[
            int, Query(ge=1, le=100, description="Cantidad de preguntas por página")
        ] = 15,
):
    """
    Este endpoint recupera preguntas de la base de datos con soporte para paginación.
    """
    return service.get_all_questions(page=page, limit=limit)
