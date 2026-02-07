from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class QuestionTypeBase(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=1,
            description="Nombre del tipo de pregunta",
            examples=["Selección directa"],
        ),
    ]
    code: Annotated[
        str,
        Field(
            min_length=1, description="Código del tipo de pregunta", examples=["DIRECT"]
        ),
    ]


# PRIVADO
class QuestionTypeRead(QuestionTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# PUBLIC
class QuestionTypeCodeOnly(BaseModel):
    code: Annotated[
        str,
        Field(description="Código del tipo de pregunta", examples=["DIRECT"]),
    ]

    model_config = ConfigDict(from_attributes=True)


class QuestionTypePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
