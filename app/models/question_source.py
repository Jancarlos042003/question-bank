from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.source import Source


class QuestionSource(Base):
    __tablename__ = "question_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"), nullable=False, index=True
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id"), nullable=False, index=True
    )
    page: Mapped[int] = mapped_column(Integer, nullable=False)

    question: Mapped["Question"] = relationship(back_populates="question_sources")
    source: Mapped["Source"] = relationship(back_populates="question_sources", lazy="joined")
