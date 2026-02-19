import hashlib
import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.question.repository import QuestionRepository
from app.api.v1.question.schemas import (
    QuestionChoicesSectionResponse,
    QuestionChoicesUpdate,
    QuestionContentsSectionResponse,
    QuestionContentsUpdate,
    QuestionCreateInput,
    QuestionDetailPublic,
    QuestionSolutionsSectionResponse,
    QuestionSolutionsUpdate,
    QuestionSourcesUpdate,
    QuestionSummaryPublic,
    QuestionUpdate,
)
from app.api.v1.question_content.schemas import ContentType, QuestionContentCreateInput
from app.core.exceptions.domain import (
    DuplicateValueError,
    ForeignKeyViolationError,
    ResourceNotFoundException,
)
from app.core.exceptions.technical import DeleteError, PersistenceError, RetrievalError
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

    def update_question(self, question_id: int, question: QuestionUpdate):
        update_data = question.model_dump(exclude_unset=True)

        if "area_ids" in update_data:
            area_ids = update_data.pop("area_ids")
            update_data["areas"] = self.area_service.get_areas(area_ids)

        return self._update_question_detail(
            question_id=question_id, update_data=update_data
        )

    def update_question_contents(
        self, question_id: int, payload: QuestionContentsUpdate
    ):
        self._ensure_question_exists(question_id)

        question_hash = self._generate_question_hash(contents=payload.contents)
        contents = [
            QuestionContent(type=c.type, value=c.value, order=c.order, label=c.label)
            for c in payload.contents
        ]
        try:
            self.question_repository.replace_question_contents_db(
                question_id=question_id, contents=contents, question_hash=question_hash
            )
            db_contents = self.question_repository.get_question_contents_db(question_id)
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar contents de la pregunta")
            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23505":
                raise DuplicateValueError(
                    "La pregunta ya existe en la base de datos"
                ) from e
            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError(
                "Error al actualizar contenido de la pregunta en la base de datos."
            ) from e
        except SQLAlchemyError as e:
            logger.exception(
                "Error al actualizar contents de la pregunta con ID %s", question_id
            )
            raise PersistenceError(
                f"Error al actualizar contenido de la pregunta con ID {question_id}"
            ) from e

        self._sign_contents(db_contents)
        return QuestionContentsSectionResponse(id=question_id, contents=db_contents)

    def update_question_choices(self, question_id: int, payload: QuestionChoicesUpdate):
        self._ensure_question_exists(question_id)

        choices = [
            Choice(
                label=c.label,
                is_correct=c.is_correct,
                contents=[
                    ChoiceContent(type=i.type, value=i.value, order=i.order)
                    for i in c.contents
                ],
            )
            for c in payload.choices
        ]
        try:
            self.question_repository.replace_question_choices_db(
                question_id=question_id, choices=choices
            )
            db_choices = self.question_repository.get_question_choices_db(question_id)
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar choices de la pregunta")
            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError(
                "Error al actualizar alternativas de la pregunta en la base de datos."
            ) from e
        except SQLAlchemyError as e:
            logger.exception(
                "Error al actualizar choices de la pregunta con ID %s", question_id
            )
            raise PersistenceError(
                f"Error al actualizar alternativas de la pregunta con ID {question_id}"
            ) from e

        for choice in db_choices:
            self._sign_contents(choice.contents)
        return QuestionChoicesSectionResponse(id=question_id, choices=db_choices)

    def update_question_solutions(
        self, question_id: int, payload: QuestionSolutionsUpdate
    ):
        self._ensure_question_exists(question_id)

        solutions = [
            Solution(
                contents=[
                    SolutionContent(type=i.type, value=i.value, order=i.order)
                    for i in solution.contents
                ]
            )
            for solution in payload.solutions
        ]
        try:
            self.question_repository.replace_question_solutions_db(
                question_id=question_id, solutions=solutions
            )
            db_solutions = self.question_repository.get_question_solutions_db(
                question_id
            )
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar solutions de la pregunta")
            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError(
                "Error al actualizar soluciones de la pregunta en la base de datos."
            ) from e
        except SQLAlchemyError as e:
            logger.exception(
                "Error al actualizar solutions de la pregunta con ID %s", question_id
            )
            raise PersistenceError(
                f"Error al actualizar soluciones de la pregunta con ID {question_id}"
            ) from e

        for solution in db_solutions:
            self._sign_contents(solution.contents)
        return QuestionSolutionsSectionResponse(id=question_id, solutions=db_solutions)

    def update_question_sources(self, question_id: int, payload: QuestionSourcesUpdate):
        self._ensure_question_exists(question_id)

        source_ids = [item.source_id for item in payload.sources]
        self.source_service.get_sources_by_ids(source_ids)

        question_sources = [
            QuestionSource(
                source_id=item.source_id,
                page=item.page,
            )
            for item in payload.sources
        ]
        try:
            self.question_repository.replace_question_sources_db(
                question_id=question_id, question_sources=question_sources
            )
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar sources de la pregunta")
            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError(
                "Error al actualizar fuentes de la pregunta en la base de datos."
            ) from e
        except SQLAlchemyError as e:
            logger.exception(
                "Error al actualizar sources de la pregunta con ID %s", question_id
            )
            raise PersistenceError(
                f"Error al actualizar fuentes de la pregunta con ID {question_id}"
            ) from e

        return None

    def _update_question_detail(self, question_id: int, update_data: dict):
        """Actualiza parcialmente una pregunta por su ID."""
        updated_question = self._update_question_entity(
            question_id=question_id, update_data=update_data
        )
        self._sign_question_images(updated_question, "full")
        return QuestionDetailPublic.model_validate(updated_question)

    def _update_question_entity(self, question_id: int, update_data: dict):
        """"""
        try:
            updated_question = self.question_repository.update_question_db(
                question_id=question_id, update_data=update_data
            )

        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar la pregunta")

            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23505":
                raise DuplicateValueError(
                    "La pregunta ya existe en la base de datos"
                ) from e

            if pgcode == "23503":
                raise ForeignKeyViolationError("La clave foránea no existe") from e

            raise PersistenceError(
                "Error al actualizar la pregunta en la base de datos."
            ) from e

        except SQLAlchemyError as e:
            logger.exception(
                "Error al actualizar la pregunta con ID %s en la base de datos",
                question_id,
            )
            raise PersistenceError(
                f"Error al actualizar la pregunta con ID {question_id}"
            ) from e

        if not updated_question:
            raise ResourceNotFoundException(
                message=f"Pregunta con ID {question_id} no encontrada."
            )

        return updated_question

    def _ensure_question_exists(self, question_id: int):
        try:
            exists = self.question_repository.question_exists_db(
                question_id=question_id
            )
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
