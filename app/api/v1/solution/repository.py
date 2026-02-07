from sqlalchemy.orm import Session

from app.models.solution import Solution


def create_solution_db(db: Session, question_id: int):
    new_solution = Solution(question_id=question_id)

    db.add(new_solution)
    db.flush()  # obtiene ID sin commit
    return new_solution
