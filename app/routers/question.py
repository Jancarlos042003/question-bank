from typing import Annotated

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.dep import get_db
from app.infrastructure.gcp.storage_adapter import GCPStorageAdapter
from app.schemas.question import QuestionCreate, QuestionRead
from app.services.image_service import ImageService
from app.services.question_service import QuestionService

question_router = APIRouter()

# Dependency injection
gcp_storage = GCPStorageAdapter()
image_service = ImageService(storage=gcp_storage)
question_service = QuestionService(image_service)


@question_router.post(
    "", response_model=QuestionRead, status_code=status.HTTP_201_CREATED
)
async def add_question(
        payload: QuestionCreate,
        db: Annotated[Session, Depends(get_db)],
        statement_images: list[UploadFile] | None = File(None),
        choice_images: list[UploadFile] | None = File(None),
        solution_images: list[UploadFile] | None = File(None),
):
    """Endpoint para crear una nueva pregunta."""
    return await question_service.create_question(
        db=db,
        question=payload,
        container_name=settings.CONTAINER_NAME,
        statement_images=statement_images,
        choice_images=choice_images,
        solution_images=solution_images,
    )


@question_router.get("", response_model=list[QuestionRead])
def all_questions(db: Annotated[Session, Depends(get_db)]):
    """Endpoint para obtener todas las preguntas."""
    return question_service.get_all_questions(db)
