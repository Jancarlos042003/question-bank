import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.question_source.repository import QuestionSourceRepository
from app.api.v1.question_source.schemas import QuestionSourceUpdateInput
from app.core.exceptions.domain import ForeignKeyViolationError, ResourceNotFoundException
from app.core.exceptions.technical import PersistenceError, RetrievalError
from app.services.question_guard_service import QuestionGuardService
from app.services.source_service import SourceService

logger = logging.getLogger(__name__)


class QuestionSourceService:
    def __init__(
            self,
            repository: QuestionSourceRepository,
            source_service: SourceService,
            question_guard_service: QuestionGuardService,
    ):
        self.repository = repository
        self.source_service = source_service
        self.question_guard_service = question_guard_service

    def update_question_source_specific(
            self,
            question_id: int,
            question_source_id: int,
            payload: QuestionSourceUpdateInput,
    ):
        self.question_guard_service.ensure_exists(question_id=question_id)

        try:
            question_source = self.repository.get_question_source_db(
                question_id=question_id,
                question_source_id=question_source_id,
            )
        except SQLAlchemyError as e:
            logger.exception(
                "Error al obtener la fuente %s de la pregunta %s",
                question_source_id,
                question_id,
            )
            raise RetrievalError("Error al obtener la fuente de la pregunta") from e

        if not question_source:
            raise ResourceNotFoundException(
                message=(
                    f"Fuente de pregunta con ID {question_source_id} no encontrada "
                    f"en la pregunta con ID {question_id}."
                )
            )

        if payload.source_id is not None:
            self.source_service.get_sources_by_ids([payload.source_id])

        try:
            self.repository.update_question_source_db(
                question_source=question_source,
                source_id=payload.source_id,
                page=payload.page,
            )
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar fuente de la pregunta")
            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError(
                "Error al actualizar la fuente de la pregunta en la base de datos."
            ) from e
        except SQLAlchemyError as e:
            logger.exception(
                "Error al actualizar fuente %s de la pregunta %s",
                question_source_id,
                question_id,
            )
            message = (
                "Error al actualizar la fuente de la pregunta "
                f"con ID {question_source_id}"
            )
            raise PersistenceError(message) from e

        return None
