from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.db.base import Base

class Difficulty(Base):
    __tablename__ = "difficulty"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    code: Mapped[int] = mapped_column(Integer, unique=True)