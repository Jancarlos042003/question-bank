from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.solution import Solution
from app.models.solution_content import SolutionContent


class SolutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_solution_db(self, question_id: int, solution_id: int):
        stmt = (
            select(Solution)
            .where(Solution.id == solution_id, Solution.question_id == question_id)
            .options(selectinload(Solution.contents))
        )
        return self.db.scalar(stmt)

    def update_solution_db(self, solution: Solution, contents: list[SolutionContent]):
        try:
            solution.contents = contents
            self.db.commit()
            self.db.refresh(solution)
            return solution
        except SQLAlchemyError:
            self.db.rollback()
            raise
