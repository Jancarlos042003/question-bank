from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.institution import Institution
    from app.models.question_source import QuestionSource


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    institution_id: Mapped[int] = mapped_column(
        ForeignKey("institutions.id"), nullable=False, index=True
    )

    institution: Mapped["Institution"] = relationship(
        back_populates="sources", lazy="joined"
    )
    question_sources: Mapped[list["QuestionSource"]] = relationship(
        back_populates="source", cascade="all, delete-orphan", lazy="selectin"
    )
