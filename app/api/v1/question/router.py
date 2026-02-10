from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.v1.question.schemas import (
    QuestionCreateInput,
    QuestionPaginatedResponse,
    QuestionStudyResponse,
)
from app.db.session import get_session
from app.infrastructure.gcp.storage_adapter import GCPStorageAdapter
from app.services.image_service import ImageService
from app.services.question_service import QuestionService

question_router = APIRouter(tags=["Question"])


# Dependency injection
def get_question_service() -> QuestionService:
    gcp_storage = GCPStorageAdapter()
    image_service = ImageService(storage=gcp_storage)
    return QuestionService(image_service)


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
        db=db,
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
    per_page: Annotated[
        int, Query(ge=1, le=100, description="Cantidad de preguntas por página")
    ] = 15,
):
    """
    Este endpoint recupera preguntas de la base de datos con soporte para paginación.
    - **page**: El número de la página que deseas consultar.
    - **per_page**: La cantidad de preguntas que deseas obtener por página.
    """
    return service.get_all_questions(db, page=page, per_page=per_page)
