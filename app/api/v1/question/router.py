from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.v1.area.repository import AreaRepository
from app.api.v1.choice.repository import ChoiceRepository
from app.api.v1.choice.schemas import ChoicePublic, ChoiceUpdateInput
from app.api.v1.institution.repository import InstitutionRepository
from app.api.v1.question.repository import QuestionRepository
from app.api.v1.question.schemas import (
    QuestionAreasSectionResponse,
    QuestionAreasSpecificUpdate,
    QuestionCreateInput,
    QuestionCreateResponse,
    QuestionDetailPublic,
    QuestionDifficultySpecificUpdate,
    QuestionPaginatedDetailResponse,
    QuestionPaginatedSummaryResponse,
    QuestionSubtopicSpecificUpdate,
    QuestionSummaryPublic,
    QuestionTypeSpecificUpdate,
)
from app.api.v1.question_content.repository import QuestionContentRepository
from app.api.v1.question_content.schemas import (
    QuestionContentResponse,
    QuestionContentUpdateInput,
)
from app.api.v1.question_source.schemas import (
    QuestionSourcePublic,
    QuestionSourceUpdateInput,
)
from app.api.v1.solution.repository import SolutionRepository
from app.api.v1.solution.schemas import SolutionPublic, SolutionUpdateInput
from app.api.v1.source.repository import SourceRepository
from app.core.config import settings
from app.db.session import get_session
from app.infrastructure.gcp.storage_adapter import GCPStorageAdapter
from app.ports.storage_port import StoragePort
from app.services.area_service import AreaService
from app.services.choice_service import ChoiceService
from app.services.image_service import ImageService
from app.services.institution_service import InstitutionService
from app.services.question_content_service import QuestionContentService
from app.services.question_service import QuestionService
from app.services.solution_service import SolutionService
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


def get_choice_service(
    db: Annotated[Session, Depends(get_session)],
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> ChoiceService:
    choice_repository = ChoiceRepository(db)
    return ChoiceService(choice_repository, image_service)


def get_solution_service(
    db: Annotated[Session, Depends(get_session)],
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> SolutionService:
    solution_repository = SolutionRepository(db)
    return SolutionService(solution_repository, image_service)


def get_question_content_service(
    db: Annotated[Session, Depends(get_session)],
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> QuestionContentService:
    question_content_repository = QuestionContentRepository(db)
    return QuestionContentService(question_content_repository, image_service)


@question_router.post(
    "", response_model=QuestionCreateResponse, status_code=status.HTTP_201_CREATED
)
async def add_question(
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


@question_router.patch(
    "/{question_id}/question-type",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Actualizar tipo de pregunta",
)
def update_question_type_specific(
    service: Annotated[QuestionService, Depends(get_question_service)],
    question_id: Annotated[int, Path(ge=1, description="ID de la pregunta")],
    payload: QuestionTypeSpecificUpdate,
):
    """Actualiza el tipo de una pregunta."""
    return service.update_question_type(question_id=question_id, payload=payload)


@question_router.patch(
    "/{question_id}/subtopic",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Actualizar subtema de pregunta",
)
def update_question_subtopic_specific(
    service: Annotated[QuestionService, Depends(get_question_service)],
    question_id: Annotated[int, Path(ge=1, description="ID de la pregunta")],
    payload: QuestionSubtopicSpecificUpdate,
):
    """Actualiza el subtema de una pregunta."""
    return service.update_question_subtopic(question_id=question_id, payload=payload)


@question_router.patch(
    "/{question_id}/difficulty",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Actualizar dificultad de pregunta",
)
def update_question_difficulty_specific(
    service: Annotated[QuestionService, Depends(get_question_service)],
    question_id: Annotated[int, Path(ge=1, description="ID de la pregunta")],
    payload: QuestionDifficultySpecificUpdate,
):
    """Actualiza la dificultad de una pregunta."""
    return service.update_question_difficulty(question_id=question_id, payload=payload)


@question_router.patch(
    "/{question_id}/areas",
    response_model=QuestionAreasSectionResponse,
    summary="Actualizar áreas de pregunta",
)
def update_question_areas_specific(
    service: Annotated[QuestionService, Depends(get_question_service)],
    question_id: Annotated[int, Path(ge=1, description="ID de la pregunta")],
    payload: QuestionAreasSpecificUpdate,
):
    """Actualiza las áreas de una pregunta."""
    return service.update_question_areas(question_id=question_id, payload=payload)


@question_router.patch(
    "/{question_id}/contents/{content_id}",
    response_model=QuestionContentResponse,
    summary="Actualizar un contenido específico de una pregunta",
)
def update_question_content(
    service: Annotated[QuestionContentService, Depends(get_question_content_service)],
    question_id: Annotated[int, Path(ge=1, description="ID de la pregunta")],
    content_id: Annotated[int, Path(ge=1, description="ID del contenido")],
    payload: QuestionContentUpdateInput,
):
    """Actualiza un contenido específico de una pregunta."""
    return service.update_question_content(
        question_id=question_id,
        content_id=content_id,
        payload=payload,
    )


@question_router.patch(
    "/{question_id}/choices/{choice_id}",
    response_model=ChoicePublic,
    summary="Actualizar una alternativa específica",
)
def update_choice(
    service: Annotated[ChoiceService, Depends(get_choice_service)],
    question_id: Annotated[int, Path(ge=1, description="ID de la pregunta")],
    choice_id: Annotated[int, Path(ge=1, description="ID de la alternativa")],
    payload: ChoiceUpdateInput,
):
    """Actualiza una alternativa específica de una pregunta."""
    return service.update_choice(
        question_id=question_id, choice_id=choice_id, payload=payload
    )


@question_router.patch(
    "/{question_id}/solutions/{solution_id}",
    response_model=SolutionPublic,
    summary="Actualizar una solución específica",
)
def update_solution(
    service: Annotated[SolutionService, Depends(get_solution_service)],
    question_id: Annotated[int, Path(ge=1, description="ID de la pregunta")],
    solution_id: Annotated[int, Path(ge=1, description="ID de la solución")],
    payload: SolutionUpdateInput,
):
    """Actualiza una solución específica de una pregunta."""
    return service.update_solution(
        question_id=question_id, solution_id=solution_id, payload=payload
    )


@question_router.patch(
    "/{question_id}/sources/{question_source_id}",
    response_model=QuestionSourcePublic,
    summary="Actualizar una fuente específica de pregunta",
)
def update_question_source_specific(
    service: Annotated[QuestionService, Depends(get_question_service)],
    question_id: Annotated[int, Path(ge=1, description="ID de la pregunta")],
    question_source_id: Annotated[
        int, Path(ge=1, description="ID de la fuente de la pregunta")
    ],
    payload: QuestionSourceUpdateInput,
):
    """Actualiza una fuente específica de una pregunta."""
    return service.update_question_source_specific(
        question_id=question_id, question_source_id=question_source_id, payload=payload
    )


@question_router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una pregunta",
)
def delete_question(
    service: Annotated[QuestionService, Depends(get_question_service)],
    question_id: Annotated[int, Path(ge=1, description="ID de la pregunta")],
):
    """Elimina una pregunta por su ID."""
    return service.delete_question(question_id=question_id)
