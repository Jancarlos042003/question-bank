from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class AssessmentBase(BaseModel):
    name: str
    year: int
    assessment_type_id: int
    period_id: int
    sequence_number: Annotated[
        int | None, Field(default=None, description="Indica el número de evaluación")
    ]
    area_id: Annotated[
        int | None,
        Field(
            default=None,
            description="Especifica a que área pertenece o es de área general(NULL)",
        ),
    ]
    modality_id: Annotated[int | None, Field(default=None)]


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentRead(AssessmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
