from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.db.base import Base

class Period(Base):
    __tablename__ = "periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(10))
    order_no: Mapped[int] = mapped_column(Integer, unique=True)