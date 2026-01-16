from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from typing import List
from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    statement: Mapped[dict] = mapped_column(JSONB, nullable=False)
    solution: Mapped[dict] = mapped_column(JSONB, nullable=False)
    difficulty_id: Mapped[int] = mapped_column(ForeignKey("difficulty.id"))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), nullable=False)
    type_question_id: Mapped[int] = mapped_column(ForeignKey("types_questions.id"))

    difficulty: Mapped["Difficulty"] = relationship()
    topic: Mapped["Topic"] = relationship()
    exam: Mapped["Exam"] = relationship()
    type_question: Mapped["TypeQuestion"] = relationship()

    choices: Mapped[List["Choice"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan"
    )