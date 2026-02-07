from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class SubtopicBase(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=1,
            description="Nombre del subtema",
            examples=["La Biología y la materia viviente"],
        ),
    ]


# PRIVADO
class SubtopicCreate(SubtopicBase):
    topic_id: Annotated[
        int, Field(gt=0, description="ID del tema al que pertenece", examples=[1])
    ]


class SubtopicUpdate(SubtopicBase):
    pass


# PUBLIC
class SubtopicPublic(SubtopicBase):
    name: Annotated[
        str,
        Field(
            description="Nombre del subtema",
            examples=["La Biología y la materia viviente"],
        ),
    ]

    model_config = ConfigDict(from_attributes=True)
