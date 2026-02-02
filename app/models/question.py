from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.assessment import Assessment
    from app.models.choice import Choice
    from app.models.difficulty import Difficulty
    from app.models.question_type import QuestionType
    from app.models.subtopic import Subtopic
    from app.models.topic import Topic


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_number: Mapped[int | None] = mapped_column(Integer)
    question_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    statement: Mapped[dict] = mapped_column(JSONB)
    solution: Mapped[dict] = mapped_column(JSONB)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), index=True)
    subtopic_id: Mapped[int | None] = mapped_column(ForeignKey("subtopics.id"), index=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), index=True)
    question_type_id: Mapped[int] = mapped_column(ForeignKey("question_types.id"), index=True)
    difficulty_id: Mapped[int] = mapped_column(ForeignKey("difficulties.id"), index=True)

    topic: Mapped["Topic"] = relationship()
    subtopic: Mapped["Subtopic"] = relationship()
    assessment: Mapped["Assessment"] = relationship()
    question_type: Mapped["QuestionType"] = relationship()
    difficulty: Mapped["Difficulty"] = relationship()

    choices: Mapped[List["Choice"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
