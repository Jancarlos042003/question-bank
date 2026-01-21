import hashlib

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.choice import Choice
from app.models.question import Question
from app.schemas.question import (
    Statement,
    QuestionCreate,
    StatementWithItems,
    MatchingStatement,
    QuestionRead,
)


def create_question(db: Session, question: QuestionCreate):
    try:
        # 1. Crear pregunta
        # Convertimos el modelo de pydantic en un dict
        question_dict = question.model_dump(exclude={"choices"}, mode="json")
        question_dict["question_hash"] = generate_question_hash(
            statement=question.statement
        )

        new_question = Question(**question_dict)
        db.add(new_question)
        db.flush()  # obtiene ID sin commit

        # 2. Crear respuestas
        choices_orm = [
            Choice(question_id=new_question.id, **choice.model_dump(mode="json"))
            for choice in question.choices
        ]

        db.add_all(choices_orm)

        db.commit()
        db.refresh(new_question)

        return QuestionRead.model_validate(new_question)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear la pregunta")


def get_all_questions(db: Session):
    stmt = select(Question)
    return db.execute(stmt).scalars().all()


def generate_question_hash(statement: Statement) -> str:
    # payload = {
    #     "statement": statement.text.strip().lower(),
    #     "image_urls": sorted(statement.image_urls or [])
    # }

    base = statement.text.strip().lower()

    if isinstance(statement, StatementWithItems):
        items = "|".join(f"{i.id.lower()}:{i.content.lower()}" for i in statement.items)
        base += f"|{items}"

    elif isinstance(statement, MatchingStatement):
        left = "|".join(
            f"{i.id.strip().lower()}:{i.content.strip().lower()}"
            for i in statement.left_column
        )
        right = "|".join(
            f"{i.id.strip().lower()}:{i.content.strip().lower()}"
            for i in statement.right_column
        )
        base += f"|{left}|{right}"

    # # Verifica si tiene items
    # if statement.items:
    #     payload["items"] = sorted([
    #         {
    #             "id": item.id,
    #             "content": item.content.strip().lower()
    #         }
    #         for item in statement.items
    #     ], key=lambda item: item["content"])
    #
    # # Verifica si existen las columnas left_column y right_column
    # if statement.left_column and statement.right_column:
    #     payload["left_column"] = sorted([
    #         {
    #             "id": item.id,
    #             "content": item.content.strip().lower()
    #         }
    #         for item in statement.left_column
    #     ], key=lambda item: item["content"])
    #
    #     payload["right_column"] = sorted([
    #         {
    #             "id": item.id,
    #             "content": item.content.strip().lower()
    #         }
    #         for item in statement.right_column
    #     ], key=lambda item: item["content"])

    # serialized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
