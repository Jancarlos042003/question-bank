from typing import List

from sqlalchemy.orm import Session

from app.api.v1.solution_content.shemas import SolutionContentCreateInput
from app.models.solution_content import SolutionContent


def create_solution_content_db(
    db: Session, solution_id: int, contents: List[SolutionContentCreateInput]
):
    solution_contents = [
        SolutionContent(solution_id=solution_id, **c.model_dump()) for c in contents
    ]

    db.add_all(solution_contents)
    db.commit()
    # db.refresh(solution_contents)
    return solution_contents
