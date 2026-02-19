import hashlib
import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.question.repository import QuestionRepository
from app.api.v1.question.schemas import (
    QuestionCreateInput,
    QuestionSummaryPublic,
    QuestionDetailPublic,
)
from app.api.v1.question_content.schemas import ContentType, QuestionContentCreateInput
from app.core.exceptions.domain import (
    DuplicateValueError,
    ForeignKeyViolationError,
    ResourceNotFoundException,
)
from app.core.exceptions.technical import PersistenceError, RetrievalError
from app.models.choice import Choice
from app.models.choice_content import ChoiceContent
from app.models.question import Question
from app.models.question_content import QuestionContent
from app.models.question_source import QuestionSource
from app.models.solution import Solution
from app.models.solution_content import SolutionContent
from app.services.area_service import AreaService
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
        question_hash = self._generate_question_hash(contents=question.contents)

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

    def _generate_question_hash(
            self, contents: list[QuestionContentCreateInput]
    ) -> str:
        base = ""
        for i in contents:
            if i.type == ContentType.IMAGE:
                break

            base += i.value.strip().lower()

        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def _sign_question_images(self, question, view):
        """Genera URLs firmadas para todas las imágenes de una pregunta."""
        # Firmar imágenes en contents
        self._sign_contents(question.contents)

        if view == "full":
            # Firmar imágenes en choices
            for choice in question.choices:
                self._sign_contents(choice.contents)

            # Firmar imágenes en solutions
            for solution in question.solutions:
                self._sign_contents(solution.contents)

    def _sign_contents(self, contents: list):
        """Firma las URLs de los contenidos de tipo imagen."""
        for content in contents:
            if content.type == ContentType.IMAGE:
                content.value = self.image_service.generate_signature(
                    storage_object_name=content.value
                )
