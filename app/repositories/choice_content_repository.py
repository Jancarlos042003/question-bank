from typing import List

from sqlalchemy.orm import Session

from app.api.v1.choice_content.schemas import ChoiceContentCreateInput
from app.models.choice_content import ChoiceContent


def create_choice_content_db(
    db: Session, choice_id: int, contents: List[ChoiceContentCreateInput]
):
    choice_contents = [
        ChoiceContent(choice_id=choice_id, **c.model_dump()) for c in contents
    ]

    db.add_all(choice_contents)
    db.commit()
    # db.refresh(choice_contents)
    return choice_contents
