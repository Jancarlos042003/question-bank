from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.solution import Solution


class ContentType(StrEnum):
    TEXT = "text"
    IMAGE = "image"


class SolutionContent(Base):
    __tablename__ = "solution_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[ContentType] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    solution_id: Mapped[int] = mapped_column(ForeignKey("solutions.id"), index=True)

    solution: Mapped["Solution"] = relationship(back_populates="contents")
