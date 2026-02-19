from sqlalchemy import Column, ForeignKey, Table

from app.db.base import Base

question_areas = Table(
    "question_areas",
    Base.metadata,
    Column(
        "question_id",
        ForeignKey("questions.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
    Column(
        "area_id",
        ForeignKey("areas.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)
