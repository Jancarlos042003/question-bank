from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.db.base import Base

class TypeQuestion(Base):
    __tablename__ = "types_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    code: Mapped[str] = mapped_column(String(20), unique=True)