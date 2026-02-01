import hashlib

from fastapi import File, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.choice.repository import create_choices_db
from app.api.v1.question.repository import create_question_db, get_all_questions_db
from app.api.v1.question.schemas import (
    MatchingStatementCreate,
    QuestionCreate,
    StatementCreate,
    StatementWithItemsCreate,
)
from app.services.image_service import ImageService


class QuestionService:
    def __init__(self, image_service: ImageService):
        self.image_service = image_service

    async def create_question(
            self,
            db: Session,
            question: QuestionCreate,
            container_name: str,
            statement_images: list[UploadFile] | None = File(None),
            choice_images: list[UploadFile] | None = File(None),
            solution_images: list[UploadFile] | None = File(None),
    ):
        # Validar contenido de choices según si hay imágenes o no
        if choice_images:
            # Si se pasan imágenes, validar que la cantidad coincida
            if len(choice_images) != len(question.choices):
                raise HTTPException(
                    status_code=400,
                    detail="El número de imágenes de choices debe coincidir con el número de choices",
                )

            # Validar que cada choice tenga contenido o imagen
            for i, choice in enumerate(question.choices):
                has_content = choice.content and choice.content.strip()
                # Verificar que la imagen existe Y tiene contenido
                has_image = choice_images[i] is not None and choice_images[i].size > 0

                if not has_content and not has_image:
                    raise HTTPException(
                        status_code=400,
                        detail=f"El choice '{choice.label}' debe tener contenido de texto o una imagen",
                    )
        else:
            # Si NO se pasan imágenes, validar que todos los choices tengan contenido
            for choice in question.choices:
                if not choice.content or not choice.content.strip():
                    raise HTTPException(
                        status_code=400,
                        detail=f"El choice '{choice.label}' debe tener contenido de texto cuando no se proporciona imagen",
                    )

        # SUBIR IMÁGENES
        course = question.subject.label

        statement_paths = await self.image_service.upload_images(
            images=statement_images,
            storage_container_name=container_name,
            destination=f"unmsm/courses/{course}/statements",
        )

        choice_paths = await self.image_service.upload_images(
            images=choice_images,
            storage_container_name=container_name,
            destination=f"unmsm/courses/{course}/choices",
        )

        solution_paths = await self.image_service.upload_images(
            images=solution_images,
            storage_container_name=container_name,
            destination=f"unmsm/courses/{course}/solutions",
        )

        # PREPARAR DATOS
        question_hash = self._generate_question_hash(statement=question.statement)

        statement_data = question.statement.model_dump(mode="json")
        if statement_paths:
            statement_data["image_paths"] = statement_paths

        solution_data = question.solution.model_dump(mode="json")
        if solution_paths:
            solution_data["image_paths"] = solution_paths

        # CREAR EN BD (transacción)
        try:
            # Crear pregunta
            question_data = {
                "question_number": question.question_number,
                "question_hash": question_hash,
                "statement": statement_data,
                "solution": solution_data,
                "topic_id": question.topic_id,
                "assessment_id": question.assessment_id,
                "question_type_id": question.question_type_id,
            }

            new_question = create_question_db(db, question_data)

            # Crear choices
            choices_data = [
                {
                    "label": choice.label,
                    "content": choice.content,
                    "is_correct": choice.is_correct,
                    "image_path": choice_paths[i] if choice_paths else None,
                    "question_id": new_question.id,
                }
                for i, choice in enumerate(question.choices)
            ]

            create_choices_db(db, choices_data)

            db.commit()
            db.refresh(new_question)

            return new_question
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="Error al crear la pregunta en la base de datos"
            )

    def get_all_questions(self, db: Session):
        """Obtiene todas las preguntas."""
        return get_all_questions_db(db)

    def _generate_question_hash(self, statement: StatementCreate) -> str:
        base = statement.text.strip().lower()

        if isinstance(statement, StatementWithItemsCreate):
            items = "|".join(
                f"{i.id.lower()}:{i.content.lower()}" for i in statement.items
            )
            base += f"|{items}"

        elif isinstance(statement, MatchingStatementCreate):
            left = "|".join(
                f"{i.id.strip().lower()}:{i.content.strip().lower()}"
                for i in statement.left_column
            )
            right = "|".join(
                f"{i.id.strip().lower()}:{i.content.strip().lower()}"
                for i in statement.right_column
            )
            base += f"|{left}|{right}"

        return hashlib.sha256(base.encode("utf-8")).hexdigest()
