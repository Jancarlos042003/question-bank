from sqlalchemy.orm import Session

from app.models.choice import Choice


def create_choice_db(db: Session, question_id: int, is_correct: bool):
    """Crea choices en la BD."""
    new_choice = Choice(question_id=question_id, is_correct=is_correct)

    db.add(new_choice)
    db.flush()  # obtiene ID sin commit
    return new_choice
