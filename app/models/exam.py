from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from app.db.base import Base


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer)
    exam_number: Mapped[int] = mapped_column(Integer)
    type_exam_id: Mapped[int] = mapped_column(ForeignKey("types_exams.id"))
    period_id: Mapped[int] = mapped_column(ForeignKey("periods.id"))
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"))

    type_exam: Mapped["TypeExam"] = relationship()
    period: Mapped["Period"] = relationship()
    area: Mapped["Area"] = relationship()