from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.content_type import ContentType

if TYPE_CHECKING:
    from app.models.solution import Solution


class SolutionContent(Base):
    __tablename__ = "solution_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[ContentType] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    solution_id: Mapped[int] = mapped_column(
        ForeignKey("solutions.id", ondelete="CASCADE"), index=True
    )

    solution: Mapped["Solution"] = relationship(back_populates="contents")
