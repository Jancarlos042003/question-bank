from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class TopicBase(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=1, description="Nombre del curso", examples=["Nombre del curso"]
        ),
    ]
    description: Annotated[
        str,
        Field(
            min_length=10,
            description="Descripción del curso",
            examples=["Descripción del curso"],
        ),
    ]


# PRIVADO
class TopicCreate(TopicBase):
    course_id: Annotated[
        int, Field(description="ID del curso al que pertenece", examples=[1])
    ]


class TopicResponse(TopicBase):
    id: int
    course_id: Annotated[int, Field(description="ID del curso al que pertenece")]

    model_config = ConfigDict(from_attributes=True)


class TopicUpdate(BaseModel):
    name: Annotated[
        str | None, Field(default=None, min_length=1, description="Nombre del curso")
    ]
    description: Annotated[
        str | None,
        Field(default=None, min_length=10, description="Descripción del curso"),
    ]


# PÚBLICO
class TopicPublic(BaseModel):
    name: Annotated[str, Field(description="Nombre del curso")]

    model_config = ConfigDict(from_attributes=True)


class TopicPublicDetailed(TopicBase):
    model_config = ConfigDict(from_attributes=True)
