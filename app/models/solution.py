from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.question import Question
from app.models.solution_content import SolutionContent


class Solution(Base):
    __tablename__ = "solutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)

    contents: Mapped[list["SolutionContent"]] = relationship(
        back_populates="solution", cascade="all, delete-orphan", lazy="selectin"
    )
    question: Mapped["Question"] = relationship(back_populates="solution")
