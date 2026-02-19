import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.question.schemas import (
    QuestionAreasSectionResponse,
    QuestionAreasSpecificUpdate,
    QuestionCreateInput,
    QuestionDetailPublic,
    QuestionDifficultySpecificUpdate,
    QuestionSubtopicSpecificUpdate,
    QuestionSummaryPublic,
    QuestionTypeSpecificUpdate,
)
from app.core.exceptions.domain import (
    DuplicateValueError,
    ForeignKeyViolationError,
    ResourceNotFoundException,
)
from app.core.exceptions.technical import DeleteError, PersistenceError, RetrievalError
from app.domain.question.hash import generate_question_hash
from app.repositories.question_repository import QuestionRepository
from app.models.choice import Choice
from app.models.choice_content import ChoiceContent
from app.models.question import Question
from app.models.question_content import QuestionContent
from app.models.question_source import QuestionSource
from app.models.solution import Solution
from app.models.solution_content import SolutionContent
from app.services.area_service import AreaService
from app.services.content_signer import sign_image_contents
from app.services.image_service import ImageService
from app.services.source_service import SourceService

logger = logging.getLogger(__name__)


class QuestionService:
    def __init__(
            self,
            question_repository: QuestionRepository,
            area_service: AreaService,
            source_service: SourceService,
            image_service: ImageService,
    ):
        self.question_repository = question_repository
        self.area_service = area_service
        self.source_service = source_service
        self.image_service = image_service

    async def create_question(self, question: QuestionCreateInput):
        question_hash = generate_question_hash(question.contents)

        areas = self.area_service.get_areas(question.area_ids)
        sources_ids = [
            question_source.source_id for question_source in question.sources
        ]
        valid_sources = self.source_service.get_sources_by_ids(sources_ids)
        source_by_id = {source.id: source for source in valid_sources}

        try:
            # Crear solución con contenidos
            solutions = []
            for solution in question.solutions:
                solution_contents = [
                    SolutionContent(type=i.type, value=i.value, order=i.order)
                    for i in solution.contents
                ]
                solution = Solution(contents=solution_contents)
                solutions.append(solution)

            # Crear opciones con contenidos
            choices = [
                Choice(
                    label=c.label,
                    is_correct=c.is_correct,
                    contents=[
                        ChoiceContent(type=i.type, value=i.value, order=i.order)
                        for i in c.contents
                    ],
                )
                for c in question.choices
            ]

            # Crear contenido de la pregunta
            question_contents = [
                QuestionContent(type=c.type, value=c.value, order=c.order)
                for c in question.contents
            ]

            question_sources = [
                QuestionSource(
                    source_id=question_source.source_id,
                    page=question_source.page,
                    source=source_by_id[question_source.source_id],
                )
                for question_source in question.sources
            ]

            # ✅ Crear pregunta con TODAS las relaciones de una vez
            new_question = Question(
                question_type_id=question.question_type_id,
                subtopic_id=question.subtopic_id,
                difficulty_id=question.difficulty_id,
                question_hash=question_hash,
                contents=question_contents,
                solutions=solutions,
                choices=choices,
                areas=areas,
                question_sources=question_sources,
            )

            return self.question_repository.create_question_db(new_question)
        except IntegrityError as e:
            # Ya logueas stacktrace.
            logger.exception("IntegrityError al crear la pregunta")

            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23505":
                raise DuplicateValueError(
                    "La pregunta ya existe en la base de datos"
                ) from e

            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError(
                "Error al crear la pregunta en la base de datos."
            ) from e

        except SQLAlchemyError as e:
            logger.exception("Error al crear la pregunta en la base de datos")
            raise PersistenceError(
                message="Error al crear la pregunta en la base de datos."
            ) from e

    def get_all_questions(self, page: int, limit: int, view: str):
        """Obtiene todas las preguntas."""
        try:
            questions = self.question_repository.get_questions_db(
                page=page, limit=limit, view=view
            )
        except SQLAlchemyError as e:
            logger.exception("Error al obtener las preguntas")
            raise RetrievalError("Error al obtener las preguntas") from e

        # Generar URLs firmadas para todas las imágenes
        for question in questions.items:
            self._sign_question_images(question, view)

        return questions

    def get_question(self, question_id: int, view: str):
        try:
            question = self.question_repository.get_question_db(
                question_id=question_id, view=view
            )
        except SQLAlchemyError as e:
            logger.exception("Error al obtener la pregunta con ID %s", question_id)
            raise RetrievalError(
                f"Error al obtener la pregunta con ID {question_id}"
            ) from e

        if not question:
            raise ResourceNotFoundException(
                message=f"Pregunta con ID {question_id} no encontrada."
            )

        self._sign_question_images(question, view)

        if view == "summary":
            return QuestionSummaryPublic.model_validate(question)

        return QuestionDetailPublic.model_validate(question)

    def update_question_type(
            self, question_id: int, payload: QuestionTypeSpecificUpdate
    ):
        self._update_question_fields(
            question_id=question_id,
            update_data={"question_type_id": payload.question_type_id},
        )
        return None

    def update_question_subtopic(
            self, question_id: int, payload: QuestionSubtopicSpecificUpdate
    ):
        self._update_question_fields(
            question_id=question_id, update_data={"subtopic_id": payload.subtopic_id}
        )
        return None

    def update_question_difficulty(
            self, question_id: int, payload: QuestionDifficultySpecificUpdate
    ):
        self._update_question_fields(
            question_id=question_id,
            update_data={"difficulty_id": payload.difficulty_id},
        )
        return None

    def update_question_areas(
            self, question_id: int, payload: QuestionAreasSpecificUpdate
    ):
        areas = self.area_service.get_areas(payload.area_ids)
        updated_question = self._update_question_fields(
            question_id=question_id, update_data={"areas": areas}
        )
        return QuestionAreasSectionResponse.model_validate(updated_question)

    def _update_question_fields(self, question_id: int, update_data: dict):
        try:
            updated_question = self.question_repository.update_question_fields_db(
                question_id=question_id, update_data=update_data
            )
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar campos de la pregunta")

            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError(
                "Error al actualizar campos de la pregunta en la base de datos."
            ) from e
        except SQLAlchemyError as e:
            logger.exception(
                "Error al actualizar campos de la pregunta con ID %s", question_id
            )
            raise PersistenceError(
                f"Error al actualizar campos de la pregunta con ID {question_id}"
            ) from e

        if not updated_question:
            raise ResourceNotFoundException(
                message=f"Pregunta con ID {question_id} no encontrada."
            )

        return updated_question

    def delete_question(self, question_id: int):
        try:
            deleted_question = self.question_repository.delete_question_db(
                question_id=question_id
            )
        except SQLAlchemyError as e:
            logger.exception("Error al eliminar la pregunta con ID %s", question_id)
            raise DeleteError(
                f"Error al eliminar la pregunta con ID {question_id}"
            ) from e

        if not deleted_question:
            raise ResourceNotFoundException(
                message=f"Pregunta con ID {question_id} no encontrada."
            )

        return deleted_question

    def _sign_question_images(self, question, view):
        """Genera URLs firmadas para todas las imágenes de una pregunta."""
        # Firmar imágenes en contents
        sign_image_contents(question.contents, self.image_service.generate_signature)

        if view == "full":
            # Firmar imágenes en choices
            for choice in question.choices:
                sign_image_contents(choice.contents, self.image_service.generate_signature)

            # Firmar imágenes en solutions
            for solution in question.solutions:
                sign_image_contents(
                    solution.contents, self.image_service.generate_signature
                )
