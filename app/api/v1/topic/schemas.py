from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.course.schemas import CoursePublic, CourseResponse


class TopicBase(BaseModel):
    name: Annotated[
        str,
        Field(min_length=1, description="Nombre del tema", examples=["La Célula"]),
    ]
    description: Annotated[
        str,
        Field(
            min_length=10,
            description="Descripción del tema",
            examples=["Descripción del tema"],
        ),
    ]


# PRIVADO
class TopicCreate(TopicBase):
    course_id: Annotated[
        int, Field(description="ID del curso al que pertenece", examples=[1])
    ]


class TopicUpdate(BaseModel):
    name: Annotated[
        str | None,
        Field(
            default=None,
            min_length=1,
            description="Nombre del tema",
            examples=["La Célula"],
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            default=None,
            min_length=10,
            description="Descripción del tema",
            examples=["Descripción del tema"],
        ),
    ]
    course_id: Annotated[
        int | None,
        Field(default=None, description="ID del curso al que pertenece", examples=[1]),
    ]


# PÚBLICO
class TopicPublic(TopicBase):
    id: Annotated[int, Field(description="ID del tema", examples=[1])]
    course: Annotated[CoursePublic, Field(description="Curso al que pertenece")]

    model_config = ConfigDict(from_attributes=True)


class TopicSimplePublic(BaseModel):
    id: Annotated[int, Field(description="ID del tema", examples=[1])]
    name: Annotated[
        str,
        Field(min_length=1, description="Nombre del tema", examples=["La Célula"]),
    ]

    model_config = ConfigDict(from_attributes=True)


class TopicPublicNoDescription(BaseModel):
    id: Annotated[int, Field(description="ID del tema", examples=[1])]
    name: Annotated[
        str,
        Field(min_length=1, description="Nombre del tema", examples=["La Célula"]),
    ]
    course: Annotated[CoursePublic, Field(description="Curso al que pertenece")]

    model_config = ConfigDict(from_attributes=True)


class TopicPaginatedResponse(BaseModel):
    total_count: Annotated[int, Field(description="Total de temas")]
    total_pages: Annotated[int, Field(description="Número de páginas")]
    current_page: Annotated[int, Field(description="Página actual")]
    items_count: Annotated[int, Field(description="Total de temas de la página actual")]
    has_prev: Annotated[bool, Field(description="Indica si existe una página anterior")]
    has_next: Annotated[
        bool, Field(description="Indica si existe una página siguiente")
    ]
    items: Annotated[
        list[TopicPublic],
        Field(description="Lista de preguntas de la página actual"),
    ]

    model_config = ConfigDict(from_attributes=True)
