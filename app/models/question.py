from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.question_areas import question_areas

if TYPE_CHECKING:
    from app.models.area import Area
    from app.models.choice import Choice
    from app.models.difficulty import Difficulty
    from app.models.question_content import QuestionContent
    from app.models.question_type import QuestionType
    from app.models.solution import Solution
    from app.models.subtopic import Subtopic


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    question_type_id: Mapped[int] = mapped_column(
        ForeignKey("question_types.id"), index=True
    )
    subtopic_id: Mapped[int] = mapped_column(ForeignKey("subtopics.id"), index=True)
    difficulty_id: Mapped[int] = mapped_column(
        ForeignKey("difficulties.id"), index=True
    )

    question_type: Mapped["QuestionType"] = relationship()
    subtopic: Mapped["Subtopic"] = relationship()
    difficulty: Mapped["Difficulty"] = relationship()

    areas: Mapped[list["Area"]] = relationship(
        secondary=question_areas, back_populates="questions"
    )
    choices: Mapped[list["Choice"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
    question_content: Mapped["QuestionContent"] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
    solution: Mapped["Solution"] = relationship(
        back_populates="question", cascade="all"
    )
