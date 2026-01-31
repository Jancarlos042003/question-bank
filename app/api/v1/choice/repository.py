from sqlalchemy.orm import Session

from app.models.choice import Choice


def create_choices_db(db: Session, choices_data: list[dict]) -> list[Choice]:
    """Crea choices en la BD."""
    choices = [Choice(**choice) for choice in choices_data]
    db.add_all(choices)
    return choices
