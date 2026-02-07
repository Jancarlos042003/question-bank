from typing import List

from sqlalchemy.orm import Session

from app.api.v1.question_content.schemas import QuestionContentCreateInput
from app.models.question_content import QuestionContent


def create_question_content_db(
    db: Session, question_id: int, contents: List[QuestionContentCreateInput]
):
    question_contents = [
        QuestionContent(**c.model_dump(), question_id=question_id) for c in contents
    ]

    db.add_all(question_contents)
    db.commit()
    # db.refresh(question_contents)
    return question_contents
