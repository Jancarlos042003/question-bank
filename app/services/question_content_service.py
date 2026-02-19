import logging
from types import SimpleNamespace

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.question_content.schemas import (
    QuestionContentResponse,
    QuestionContentUpdateInput,
)
from app.core.exceptions.domain import (
    DuplicateValueError,
    ForeignKeyViolationError,
    ResourceNotFoundException,
)
from app.core.exceptions.technical import PersistenceError, RetrievalError
from app.domain.question.hash import generate_question_hash
from app.repositories.question_content_repository import QuestionContentRepository
from app.services.content_signer import sign_image_contents
from app.services.image_service import ImageService
from app.services.question_guard_service import QuestionGuardService

logger = logging.getLogger(__name__)


class QuestionContentService:
    def __init__(
            self,
            repository: QuestionContentRepository,
            image_service: ImageService,
            question_guard_service: QuestionGuardService,
    ):
        self.repository = repository
        self.image_service = image_service
        self.question_guard_service = question_guard_service

    def update_question_content(
            self,
            question_id: int,
            content_id: int,
            payload: QuestionContentUpdateInput,
    ):
        self.question_guard_service.ensure_exists(question_id=question_id)

        try:
            db_content = self.repository.get_question_content_db(
                question_id=question_id,
                content_id=content_id,
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
            contents = self.repository.get_question_contents_db(question_id=question_id)
        except SQLAlchemyError as e:
            logger.exception(
                "Error al obtener contenidos de la pregunta con ID %s", question_id
            )
            raise RetrievalError("Error al obtener contenidos de la pregunta") from e

        # Se usa para generar un hash de la pregunta y detectar duplicados antes de persistir
        projected_contents = []
        for content in contents:
            if content.id == content_id:
                projected_contents.append(
                    # Simulamos el objeto QuestionContent
                    SimpleNamespace(
                        type=payload.type if payload.type is not None else content.type,
                        value=(
                            payload.value
                            if payload.value is not None
                            else content.value
                        ),
                        order=(
                            payload.order
                            if payload.order is not None
                            else content.order
                        ),
                    )
                )
                continue

            projected_contents.append(
                SimpleNamespace(
                    type=content.type,
                    value=content.value,
                    order=content.order,
                )
            )

        question_hash = generate_question_hash(projected_contents)

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

        sign_image_contents([updated_content], self.image_service.generate_signature)

        return QuestionContentResponse.model_validate(updated_content)
