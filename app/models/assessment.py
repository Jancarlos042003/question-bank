from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.area import Area
    from app.models.assessment_type import AssessmentType
    from app.models.modality import Modality
    from app.models.period import Period


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(Integer)
    sequence_number: Mapped[Optional[int]] = mapped_column(Integer)
    assessment_type_id: Mapped[int] = mapped_column(ForeignKey("assessment_types.id"))
    period_id: Mapped[int] = mapped_column(ForeignKey("periods.id"))
    area_id: Mapped[Optional[int]] = mapped_column(ForeignKey("areas.id"))
    modality_id: Mapped[Optional[int]] = mapped_column(ForeignKey("modalities.id"))

    assessment_type: Mapped["AssessmentType"] = relationship()
    period: Mapped["Period"] = relationship()
    area: Mapped["Area"] = relationship()
    modality: Mapped["Modality"] = relationship()
