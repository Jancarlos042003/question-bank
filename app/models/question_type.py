from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QuestionType(Base):
    __tablename__ = "question_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    code: Mapped[str] = mapped_column(String(20), unique=True)
