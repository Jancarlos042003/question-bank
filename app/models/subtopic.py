from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.topic import Topic

class Subtopic(Base):
    __tablename__ = "subtopics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))

    topic: Mapped["Topic"] = relationship()
