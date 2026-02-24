import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.solution.schemas import SolutionPublic, SolutionUpdateInput
from app.core.exceptions.domain import (
    ForeignKeyViolationError,
    ResourceNotFoundException,
)
from app.core.exceptions.technical import PersistenceError, RetrievalError
from app.helpers.content_signer import sign_image_contents
from app.models.solution_content import SolutionContent
from app.repositories.solution_repository import SolutionRepository
from app.services.image_service import ImageService
from app.services.question_guard_service import QuestionGuardService

logger = logging.getLogger(__name__)


class SolutionService:
    def __init__(
            self,
            repository: SolutionRepository,
            image_service: ImageService,
            question_guard_service: QuestionGuardService,
    ):
        self.repository = repository
        self.image_service = image_service
        self.question_guard_service = question_guard_service

    def update_solution(
            self,
            question_id: int,
            solution_id: int,
            payload: SolutionUpdateInput,
    ):
        self.question_guard_service.ensure_exists(question_id=question_id)

        try:
            db_solution = self.repository.get_solution_db(
                question_id=question_id, solution_id=solution_id
            )
        except SQLAlchemyError as e:
            logger.exception(
                "Error al obtener solución %s de la pregunta %s",
                solution_id,
                question_id,
            )
            raise RetrievalError("Error al obtener la solución") from e

        if not db_solution:
            raise ResourceNotFoundException(
                message=(
                    f"Solución con ID {solution_id} no encontrada "
                    f"en la pregunta con ID {question_id}."
                )
            )

        contents = [
            SolutionContent(type=item.type, value=item.value, order=item.order)
            for item in payload.contents
        ]

        try:
            updated_solution = self.repository.update_solution_db(
                solution=db_solution, contents=contents
            )
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar solución")
            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError("Error al actualizar la solución") from e
        except SQLAlchemyError as e:
            logger.exception("Error al actualizar solución")
            raise PersistenceError("Error al actualizar la solución") from e

        sign_image_contents(
            updated_solution.contents, self.image_service.generate_signature
        )

        return SolutionPublic.model_validate(updated_solution)
