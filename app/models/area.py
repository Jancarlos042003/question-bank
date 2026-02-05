from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.question_areas import question_areas

if TYPE_CHECKING:
    from app.models.question import Question


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(String(1), unique=True)

    questions: Mapped[list["Question"]] = relationship(
        secondary=question_areas, back_populates="areas"
    )
