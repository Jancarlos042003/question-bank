from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from app.db.base import Base


class Subtopic(Base):
    __tablename__ = "subtopics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))

    topic: Mapped["Topic"] = relationship()
