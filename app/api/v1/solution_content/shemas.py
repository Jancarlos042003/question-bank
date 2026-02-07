from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ContentType(StrEnum):
    TEXT = "text"
    IMAGE = "image"


class SolutionContentBase(BaseModel):
    type: Annotated[
        ContentType,
        Field(
            description="Tipo de contenido",
            examples=[ContentType.TEXT, ContentType.IMAGE],
        ),
    ]
    value: Annotated[
        str,
        Field(
            min_length=10,
            examples=["Esta es una explicación detallada de la solución."],
        ),
    ]
    order: Annotated[int, Field(description="Orden de aparición", ge=1, examples=[1])]


class SolutionContentCreateInput(SolutionContentBase):
    pass


class SolutionContentCreate(SolutionContentBase):
    solution_id: int


class SolutionContentResponse(SolutionContentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SolutionContentSimpleResponse(SolutionContentBase):
    model_config = ConfigDict(from_attributes=True)
