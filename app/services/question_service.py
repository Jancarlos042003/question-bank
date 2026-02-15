import hashlib
import logging

from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.question.repository import QuestionRepository
from app.api.v1.question.schemas import QuestionCreateInput
from app.api.v1.question_content.schemas import ContentType, QuestionContentCreateInput
from app.core.exceptions.domain import DuplicateQuestionHashError
from app.core.exceptions.technical import PersistenceError
from app.models.choice import Choice
from app.models.choice_content import ChoiceContent
from app.models.question import Question
from app.models.question_content import QuestionContent
from app.models.solution import Solution
from app.models.solution_content import SolutionContent
from app.services.area_service import AreaService
from app.services.image_service import ImageService

logger = logging.getLogger(__name__)


class QuestionService:
    def __init__(
            self,
            question_repository: QuestionRepository,
            area_service: AreaService,
            image_service: ImageService,
    ):
        self.question_repository = question_repository
        self.area_service = area_service
        self.image_service = image_service

    async def create_question(self, question: QuestionCreateInput):
        statement = ""
        for i in question.contents:
            if i.type == ContentType.IMAGE:
                break
            statement += i.value

        question_hash = self._generate_question_hash(contents=question.contents)

        areas = self.area_service.get_areas(question.area_ids)

        try:
            # Crear solución con contenidos
            solution_contents = [
                SolutionContent(type=i.type, value=i.value, order=i.order)
                for i in question.solution.contents
            ]
            solution = Solution(contents=solution_contents)

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

            # ✅ Crear pregunta con TODAS las relaciones de una vez
            new_question = Question(
                question_type_id=question.question_type_id,
                subtopic_id=question.subtopic_id,
                difficulty_id=question.difficulty_id,
                question_hash=question_hash,
                contents=question_contents,
                solution=solution,
                choices=choices,
                areas=areas,
            )

            return self.question_repository.create_question_db(new_question)
        except DuplicateQuestionHashError:
            raise DuplicateQuestionHashError(
                "La pregunta ya existe en la base de datos"
            )
        except SQLAlchemyError as e:
            logger.error("Error al crear la pregunta en la base de datos: %s", e)
            raise PersistenceError(
                message=f"Error al crear la pregunta en la base de datos."
            )

    def get_all_questions(self, page: int, limit: int):
        """Obtiene todas las preguntas."""
        questions = self.question_repository.get_questions_db(page=page, limit=limit)

        # Generar URLs firmadas para todas las imágenes
        for question in questions.items:
            self._sign_question_images(question)

        return questions

    def _generate_question_hash(
            self, contents: list[QuestionContentCreateInput]
    ) -> str:
        base = ""
        for i in contents:
            if i.type == ContentType.IMAGE:
                break

            base += i.value.strip().lower()

        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def _sign_question_images(self, question):
        """Genera URLs firmadas para todas las imágenes de una pregunta."""
        # Firmar imágenes en contents
        self._sign_contents(question.contents)

        # Firmar imágenes en choices
        for choice in question.choices:
            self._sign_contents(choice.contents)

        # Firmar imágenes en solution
        if question.solution:
            self._sign_contents(question.solution.contents)

    def _sign_contents(self, contents: list):
        """Firma las URLs de los contenidos de tipo imagen."""
        for content in contents:
            if content.type == ContentType.IMAGE:
                content.value = self.image_service.generate_signature(
                    storage_object_name=content.value
                )
