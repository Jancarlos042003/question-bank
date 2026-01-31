from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.question.schemas import QuestionCreate, QuestionRead
from app.core.config import settings
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
    "", response_model=QuestionRead, status_code=status.HTTP_201_CREATED
)
async def add_question(
        payload: Annotated[str, Form(...)],
        db: Annotated[Session, Depends(get_session)],
        service: Annotated[QuestionService, Depends(get_question_service)],
        statement_images: list[UploadFile] | None = File(None),
        choice_images: list[UploadFile] | None = File(None),
        solution_images: list[UploadFile] | None = File(None),
):
    """Endpoint para crear una nueva pregunta."""

    #  Convertir el string JSON del formulario en un objeto de Pydantic.
    question = QuestionCreate.model_validate_json(payload)

    return await service.create_question(
        db=db,
        question=question,
        container_name=settings.CONTAINER_NAME,
        statement_images=statement_images,
        choice_images=choice_images,
        solution_images=solution_images,
    )


@question_router.get("", response_model=list[QuestionRead])
def all_questions(
        db: Annotated[Session, Depends(get_session)],
        service: Annotated[QuestionService, Depends(get_question_service)],
):
    """Endpoint para obtener todas las preguntas."""
    return service.get_all_questions(db)
