from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.choice import Choice


class ContentType(StrEnum):
    TEXT = "text"
    IMAGE = "image"


class ChoiceContent(Base):
    __tablename__ = "choice_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(1), nullable=False)
    type: Mapped[ContentType] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    choice_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))

    choice: Mapped["Choice"] = relationship(back_populates="choice_content")
