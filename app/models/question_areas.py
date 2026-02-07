from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

question_areas = Table(
    "question_areas",
    Base.metadata,
    Column("question_id", ForeignKey("questions.id"), primary_key=True, index=True),
    Column("area_id", ForeignKey("areas.id"), primary_key=True, index=True),
)
