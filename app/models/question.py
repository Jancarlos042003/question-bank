from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, Optional
from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_number: Mapped[Optional[int]] = mapped_column(Integer)
    question_hash: Mapped[str] = mapped_column(String(64), unique=True)
    statement: Mapped[dict] = mapped_column(JSONB)
    solution: Mapped[dict] = mapped_column(JSONB)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"))
    question_type_id: Mapped[int] = mapped_column(ForeignKey("question_types.id"))

    topic: Mapped["Topic"] = relationship()
    assessment: Mapped["Assessment"] = relationship()
    question_type: Mapped["QuestionType"] = relationship()

    choices: Mapped[List["Choice"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan"
    )