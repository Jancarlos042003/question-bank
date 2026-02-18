from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.source import Source


class InstitutionType(StrEnum):
    UNIVERSITY = "universidad"
    EDITORIAL = "editorial"
    ACADEMY = "academia"
    OTHER = "otro"


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    type: Mapped[InstitutionType] = mapped_column(String(20), nullable=False)

    sources: Mapped[list["Source"]] = relationship(
        back_populates="institution", lazy="selectin"
    )
