import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.choice.repository import ChoiceRepository
from app.api.v1.choice.schemas import ChoicePublic, ChoiceUpdateInput
from app.api.v1.choice_content.schemas import ContentType
from app.core.exceptions.domain import (
    DuplicateChoiceContentError,
    ForeignKeyViolationError,
    NoCorrectChoiceError,
    ResourceNotFoundException,
)
from app.core.exceptions.technical import PersistenceError, RetrievalError
from app.models.choice_content import ChoiceContent
from app.services.image_service import ImageService

logger = logging.getLogger(__name__)


class ChoiceService:
    def __init__(self, repository: ChoiceRepository, image_service: ImageService):
        self.repository = repository
        self.image_service = image_service

    def update_choice(
            self,
            question_id: int,
            choice_id: int,
            payload: ChoiceUpdateInput,
    ):
        try:
            db_choice = self.repository.get_choice_db(
                question_id=question_id, choice_id=choice_id
            )
        except SQLAlchemyError as e:
            logger.exception(
                "Error al obtener alternativa %s de la pregunta %s",
                choice_id,
                question_id,
            )
            raise RetrievalError("Error al obtener la alternativa") from e

        if not db_choice:
            raise ResourceNotFoundException(
                message=(
                    f"Alternativa con ID {choice_id} no encontrada "
                    f"en la pregunta con ID {question_id}."
                )
            )

        if payload.contents is not None:
            self._validate_unique_choice_contents(
                question_id=question_id, choice_id=choice_id, contents=payload.contents
            )

        # Si se quiere desmarcar la alternativa como correcta
        if payload.is_correct is False and db_choice.is_correct:
            # Verificar que exista al menos otra alternativa correcta antes de permitir el cambio.
            self._validate_other_correct_choice_exists(question_id, choice_id)

        demote_others = payload.is_correct is True
        new_contents = None
        if payload.contents is not None:
            new_contents = [
                ChoiceContent(type=item.type, value=item.value, order=item.order)
                for item in payload.contents
            ]

        try:
            updated_choice = self.repository.update_choice_db(
                choice=db_choice,
                question_id=question_id,
                label=payload.label,
                is_correct=payload.is_correct,
                contents=new_contents,
                demote_others=demote_others,
            )
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar alternativa")
            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError("Error al actualizar la alternativa") from e
        except SQLAlchemyError as e:
            logger.exception("Error al actualizar alternativa")
            raise PersistenceError("Error al actualizar la alternativa") from e

        self._sign_contents(updated_choice.contents)
        return ChoicePublic.model_validate(updated_choice)

    def _validate_other_correct_choice_exists(self, question_id: int, choice_id: int):
        """
        Valida que exista al menos otra alternativa correcta en la pregunta,
        excluyendo la alternativa indicada por `choice_id`
        """
        try:
            correct_others = self.repository.count_correct_choices_db(
                question_id=question_id, exclude_choice_id=choice_id
            )
        except SQLAlchemyError as e:
            logger.exception("Error al validar alternativa correcta")
            raise RetrievalError("Error al validar alternativas correctas") from e

        if correct_others == 0:
            raise NoCorrectChoiceError("Debe existir al menos una alternativa correcta")

    def _validate_unique_choice_contents(
            self,
            question_id: int,
            choice_id: int,
            contents,
    ):
        """Valida que los contenidos de una alternativa sean únicos tanto dentro de la propia alternativa
        como respecto a las demás alternativas de la misma pregunta."""

        # 1
        incoming_values = [content.value.strip().lower() for content in contents]
        if len(incoming_values) != len(set(incoming_values)):
            raise DuplicateChoiceContentError(
                "Las respuestas deben ser únicas dentro de la alternativa."
            )

        try:
            other_values = self.repository.get_other_choice_content_values_db(
                question_id=question_id, choice_id=choice_id
            )
        except SQLAlchemyError as e:
            logger.exception("Error al validar contenido duplicado de alternativas")
            raise RetrievalError("Error al validar contenido de alternativas") from e

        # 2
        duplicated = [value for value in incoming_values if value in other_values]
        if duplicated:
            message = (
                "Las respuestas deben ser únicas. "
                f"Contenido duplicado: '{duplicated[0]}'"
            )
            raise DuplicateChoiceContentError(message)

    def _sign_contents(self, contents: list):
        for content in contents:
            if content.type == ContentType.IMAGE:
                content.value = self.image_service.generate_signature(
                    storage_object_name=content.value
                )
