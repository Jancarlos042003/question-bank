import hashlib
import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.question_content.repository import QuestionContentRepository
from app.api.v1.question_content.schemas import (
    ContentType,
    QuestionContentResponse,
    QuestionContentUpdateInput,
)
from app.core.exceptions.domain import (
    DuplicateValueError,
    ForeignKeyViolationError,
    ResourceNotFoundException,
)
from app.core.exceptions.technical import PersistenceError, RetrievalError
from app.services.image_service import ImageService

logger = logging.getLogger(__name__)


class QuestionContentService:
    def __init__(
            self,
            repository: QuestionContentRepository,
            image_service: ImageService,
    ):
        self.repository = repository
        self.image_service = image_service

    def update_question_content(
            self,
            question_id: int,
            content_id: int,
            payload: QuestionContentUpdateInput,
    ):
        try:
            db_content = self.repository.get_question_content_db(
                question_id=question_id, content_id=content_id
            )
        except SQLAlchemyError as e:
            logger.exception(
                "Error al obtener contenido %s de la pregunta %s",
                content_id,
                question_id,
            )
            raise RetrievalError("Error al obtener el contenido de la pregunta") from e

        if not db_content:
            raise ResourceNotFoundException(
                message=(
                    f"Contenido con ID {content_id} no encontrado "
                    f"en la pregunta con ID {question_id}."
                )
            )

        try:
            # Obtener todos los contents para recalcular `question_hash`
            contents = self.repository.get_question_contents_db(question_id=question_id)
        except SQLAlchemyError as e:
            logger.exception(
                "Error al obtener contenidos de la pregunta con ID %s", question_id
            )
            raise RetrievalError("Error al obtener contenidos de la pregunta") from e

        for content in contents:
            if content.id != content_id:
                continue

            if payload.label is not None:
                content.label = payload.label
            if payload.type is not None:
                content.type = payload.type
            if payload.value is not None:
                content.value = payload.value
            if payload.order is not None:
                content.order = payload.order
            break

        question_hash = self._generate_question_hash(contents=contents)

        try:
            updated_content = self.repository.update_question_content_db(
                content=db_content,
                label=payload.label,
                content_type=payload.type,
                value=payload.value,
                order=payload.order,
                question_hash=question_hash,
            )
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar contenido de la pregunta")
            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23505":
                raise DuplicateValueError(
                    "La pregunta ya existe en la base de datos"
                ) from e

            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError(
                "Error al actualizar el contenido de la pregunta"
            ) from e
        except SQLAlchemyError as e:
            logger.exception("Error al actualizar contenido de la pregunta")
            raise PersistenceError(
                "Error al actualizar el contenido de la pregunta"
            ) from e

        if updated_content.type == ContentType.IMAGE:
            updated_content.value = self.image_service.generate_signature(
                storage_object_name=updated_content.value
            )

        return QuestionContentResponse.model_validate(updated_content)

    def _generate_question_hash(self, contents: list) -> str:
        ordered_contents = sorted(contents, key=lambda item: item.order)
        base = ""

        for item in ordered_contents:
            if item.type == ContentType.IMAGE:
                break

            base += item.value.strip().lower()

        return hashlib.sha256(base.encode("utf-8")).hexdigest()
