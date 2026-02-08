from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ContentType(StrEnum):
    TEXT = "text"
    IMAGE = "image"


class QuestionContentBase(BaseModel):
    label: Annotated[str | None, Field(default=None, max_length=1, examples=["I"])]
    type: Annotated[
        ContentType,
        Field(
            description="Tipo de contenido",
            examples=[ContentType.TEXT, ContentType.IMAGE],
        ),
    ]
    (
        Field(
            min_length=10,
            examples=["Texto de la pregunta o el path de la imagen"],
        ),
    )
    value: Annotated[
        str,
        Field(min_length=5, examples=["Texto de la pregunta o el path de la imagen"]),
    ]
    order: Annotated[int, Field(description="Orden de aparición", ge=1, examples=[1])]


class QuestionContentCreateInput(QuestionContentBase):
    pass


class QuestionContentCreate(QuestionContentBase):
    question_id: Annotated[int, Field(examples=[10])]


class QuestionContentResponse(QuestionContentBase):
    id: Annotated[int, Field(gt=0, examples=[1])]

    model_config = ConfigDict(from_attributes=True)
