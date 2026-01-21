from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.choice import Choice
from app.schemas.choice import ChoiceCreate


def create_choice(db: Session, question_id: int, choices: List[ChoiceCreate]):
    try:
        list_new_choices = [
            Choice(
                label=choice.label,
                content=choice.content,
                image_url=choice.image_url,
                is_correct=choice.is_correct,
                question_id=question_id,
            )
            for choice in choices
        ]

        db.add_all(list_new_choices)
        db.commit()

        for choice in list_new_choices:
            db.refresh(choice)

        return list_new_choices
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al crear las respuestas de la pregunta"
        )
