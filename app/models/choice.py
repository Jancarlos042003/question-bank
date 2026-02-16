from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.choice_content import ChoiceContent
    from app.models.question import Question


class Choice(Base):
    __tablename__ = "choices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    label: Mapped[str] = mapped_column(String(1), nullable=True)  # CAMBIAR A FALSE
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    question: Mapped["Question"] = relationship(back_populates="choices")
    contents: Mapped[list["ChoiceContent"]] = relationship(
        back_populates="choice",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ChoiceContent.order",
    )
