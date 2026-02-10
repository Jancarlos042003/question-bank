import hashlib

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.area.repository import get_areas
from app.api.v1.question.repository import get_questions_db
from app.api.v1.question.schemas import QuestionCreateInput
from app.api.v1.question_content.schemas import ContentType, QuestionContentCreateInput
from app.models.choice import Choice
from app.models.choice_content import ChoiceContent
from app.models.question import Question
from app.models.question_content import QuestionContent
from app.models.solution import Solution
from app.models.solution_content import SolutionContent
from app.services.image_service import ImageService


class QuestionService:
    def __init__(self, image_service: ImageService):
        self.image_service = image_service

    async def create_question(self, db: Session, question: QuestionCreateInput):
        statement = ""
        for i in question.contents:
            if i.type == ContentType.IMAGE:
                break
            statement += i.value

        question_hash = self._generate_question_hash(contents=question.contents)
        areas = get_areas(db, question.area_ids)

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
                areas=areas,  # ✅ Asignar directamente en el constructor
            )

            # Agregar y commitear
            db.add(new_question)
            db.commit()
            db.refresh(new_question)

            return new_question
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear la pregunta en la base de datos: {str(e)}",
            )

    def get_all_questions(self, db: Session, page: int, per_page: int):
        """Obtiene todas las preguntas."""
        return get_questions_db(db, page=page, limit=per_page)

    def _generate_question_hash(
        self, contents: list[QuestionContentCreateInput]
    ) -> str:
        base = ""
        for i in contents:
            if i.type == ContentType.IMAGE:
                break

            base += i.value.strip().lower()

        return hashlib.sha256(base.encode("utf-8")).hexdigest()
