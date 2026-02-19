from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.v1.choice.schemas import ChoicePublic, ChoiceUpdateInput
from app.api.v1.question.dependencies import (
    get_choice_service,
    get_question_content_service,
    get_question_service,
    get_question_source_service,
    get_solution_service,
)
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
from app.api.v1.question_content.schemas import (
    QuestionContentResponse,
    QuestionContentUpdateInput,
)
from app.api.v1.question_source.schemas import (
    QuestionSourceUpdateInput,
)
from app.api.v1.solution.schemas import SolutionPublic, SolutionUpdateInput
from app.services.choice_service import ChoiceService
from app.services.question_content_service import QuestionContentService
from app.services.question_service import QuestionService
from app.services.question_source_service import QuestionSourceService
from app.services.solution_service import SolutionService

question_router = APIRouter(tags=["Question"])


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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Actualizar una fuente específica de pregunta",
)
def update_question_source_specific(
        service: Annotated[QuestionSourceService, Depends(get_question_source_service)],
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
    service.delete_question(question_id=question_id)
    return None
