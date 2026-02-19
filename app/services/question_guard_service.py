import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.domain import ResourceNotFoundException
from app.core.exceptions.technical import RetrievalError
from app.repositories.question_repository import QuestionRepository

logger = logging.getLogger(__name__)


class QuestionGuardService:
    def __init__(self, question_repository: QuestionRepository):
        self.question_repository = question_repository

    def ensure_exists(self, question_id: int):
        try:
            exists = self.question_repository.question_exists_db(question_id=question_id)
        except SQLAlchemyError as e:
            logger.exception(
                "Error al verificar existencia de la pregunta con ID %s", question_id
            )
            raise RetrievalError(
                f"Error al verificar la pregunta con ID {question_id}"
            ) from e

        if not exists:
            raise ResourceNotFoundException(
                message=f"Pregunta con ID {question_id} no encontrada."
            )
