from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QuestionAreas(Base):
    __tablename__ = "question_areas"

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"), primary_key=True
    )
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"), primary_key=True)
