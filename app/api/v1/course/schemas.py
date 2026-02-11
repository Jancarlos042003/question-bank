from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    name: Annotated[
        str,
        Field(min_length=1, description="Nombre del curso", examples=["Biología"]),
    ]
    code: Annotated[
        str,
        Field(
            min_length=2,
            max_length=2,
            description="Código del curso",
            examples=["BI"],
        ),
    ]


# PRIVADO
class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: Annotated[
        str | None, Field(default=None, min_length=1, description="Nombre del curso")
    ]
    code: Annotated[
        str | None,
        Field(
            default=None,
            min_length=2,
            max_length=2,
            description="Código del curso",
        ),
    ]


class CourseResponse(CourseBase):
    id: Annotated[int, Field(description="ID del curso", examples=[1])]


# PÚBLICO
class CoursePublic(BaseModel):
    name: Annotated[str, Field(description="Nombre del curso", examples=["Biología"])]
    code: Annotated[str, Field(description="Código del curso", examples=["BI"])]

    model_config = ConfigDict(from_attributes=True)
