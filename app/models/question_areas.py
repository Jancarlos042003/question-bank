from sqlalchemy import Column, ForeignKey, Table

from app.db.base import Base

question_areas = Table(
    "question_areas",
    Base.metadata,
    Column("question_id", ForeignKey("questions.id"), primary_key=True),
    Column("area_id", ForeignKey("areas.id"), primary_key=True)
)
