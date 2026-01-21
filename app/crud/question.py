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
)


def create_question(db: Session, question: QuestionCreate):
    try:
        # 1. Crear pregunta
        question_hash = generate_question_hash(statement=question.statement)

        new_question = Question(
            question_number=question.question_number,
            question_hash=question_hash,
            statement=question.statement.model_dump(mode="json"),
            solution=question.solution.model_dump(mode="json"),
            topic_id=question.topic_id,
            assessment_id=question.assessment_id,
            question_type_id=question.question_type_id,
        )

        db.add(new_question)
        db.flush()  # obtiene ID sin commit

        # 2. Crear respuestas
        choices_orm = [
            Choice(
                label=choice.label,
                content=choice.content,
                is_correct=choice.is_correct,
                image_url=choice.image_url,
                question_id=new_question.id,
            )
            for choice in question.choices
        ]

        db.add_all(choices_orm)

        db.commit()
        db.refresh(new_question)

        return new_question
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear la pregunta")


def get_all_questions(db: Session):
    stmt = select(Question)
    return db.execute(stmt).scalars().all()


def generate_question_hash(statement: Statement) -> str:
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

    return hashlib.sha256(base.encode("utf-8")).hexdigest()
