from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.v1.area.repository import AreaRepository
from app.api.v1.institution.repository import InstitutionRepository
from app.api.v1.question.repository import QuestionRepository
from app.api.v1.question.schemas import (
    QuestionCreateInput,
    QuestionCreateResponse,
    QuestionPaginatedSummaryResponse,
    QuestionPaginatedDetailResponse,
    QuestionSummaryPublic,
    QuestionDetailPublic,
)
from app.api.v1.source.repository import SourceRepository
from app.core.config import settings
from app.db.session import get_session
from app.infrastructure.gcp.storage_adapter import GCPStorageAdapter
from app.ports.storage_port import StoragePort
from app.services.area_service import AreaService
from app.services.image_service import ImageService
from app.services.institution_service import InstitutionService
from app.services.question_service import QuestionService
from app.services.source_service import SourceService

question_router = APIRouter(tags=["Question"])


# Dependency injection
def get_area_service(db: Annotated[Session, Depends(get_session)]):
    area_repository = AreaRepository(db)
    return AreaService(area_repository)


def get_gcp_storage():
    return GCPStorageAdapter()


def get_institution_service(db: Annotated[Session, Depends(get_session)]):
    institution_repository = InstitutionRepository(db)
    return InstitutionService(institution_repository)


def get_source_service(
        db: Annotated[Session, Depends(get_session)],
        institution_service: Annotated[
            InstitutionService, Depends(get_institution_service)
        ],
):
    source_repository = SourceRepository(db)
    return SourceService(source_repository, institution_service)


def get_image_service(storage: Annotated[StoragePort, Depends(get_gcp_storage)]):
    return ImageService(storage, settings.CONTAINER_NAME)


def get_question_service(
        db: Annotated[Session, Depends(get_session)],
        area_service: Annotated[AreaService, Depends(get_area_service)],
        source_service: Annotated[SourceService, Depends(get_source_service)],
        image_service: Annotated[ImageService, Depends(get_image_service)],
) -> QuestionService:
    question_repository = QuestionRepository(db)

    return QuestionService(
        question_repository, area_service, source_service, image_service
    )


@question_router.post(
    "", response_model=QuestionCreateResponse, status_code=status.HTTP_201_CREATED
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
    response_model=QuestionPaginatedSummaryResponse | QuestionPaginatedDetailResponse,
    summary="Listar preguntas",
)
def get_questions(
        service: Annotated[QuestionService, Depends(get_question_service)],
        page: Annotated[int, Query(ge=1, description="Página actual")] = 1,
        limit: Annotated[
            int, Query(ge=1, le=100, description="Cantidad de preguntas por página")
        ] = 15,
        view: Annotated[
            Literal["summary", "full"],
            Query(description="Nivel de detalle de la pregunta."),
        ] = "full",
):
    """
    Este endpoint recupera preguntas de la base de datos con soporte para paginación.

    Nivel de detalle (view):
    - `summary`: Versión resumida que no incluye alternativas ni solución.
    - `full`: Versión completa que incluye toda la información disponible.
    """
    return service.get_all_questions(page=page, limit=limit, view=view)


@question_router.get(
    "/{question_id}",
    response_model=QuestionSummaryPublic | QuestionDetailPublic,
    summary="Obtener una pregunta",
)
def get_question(
        service: Annotated[QuestionService, Depends(get_question_service)],
        question_id: Annotated[int, Path(ge=1, description="ID de la pregunta")],
        view: Annotated[
            Literal["summary", "full"],
            Query(description="Nivel de detalle de la pregunta."),
        ] = "full",
):
    """
    Obtener una pregunta por su ID.

    Nivel de detalle (view):
    - `summary`: Versión resumida que no incluye alternativas ni solución.
    - `full`: Versión completa que incluye toda la información disponible.
    """
    return service.get_question(question_id=question_id, view=view)
