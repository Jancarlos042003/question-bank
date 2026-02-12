from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.topic.schemas import TopicSimplePublic


class SubtopicBase(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=1,
            description="Nombre del subtema",
            examples=["Los Organelos Celulares"],
        ),
    ]


# PRIVADO
class SubtopicCreate(SubtopicBase):
    topic_id: Annotated[
        int, Field(gt=0, description="ID del tema al que pertenece", examples=[1])
    ]


class SubtopicUpdate(BaseModel):
    name: Annotated[
        str | None,
        Field(
            min_length=1,
            description="Nombre del subtema",
            examples=["Los Organelos Celulares"],
        ),
    ] = None
    topic_id: Annotated[
        int | None,
        Field(gt=0, description="ID del tema al que pertenece", examples=[1]),
    ] = None


# PUBLIC
class SubtopicSimplePublic(BaseModel):
    id: Annotated[int, Field(description="ID del subtema", examples=[1])]
    name: Annotated[
        str,
        Field(
            description="Nombre del subtema",
            examples=["Los Organelos Celulares"],
        ),
    ]

    model_config = ConfigDict(from_attributes=True)


class SubtopicPublic(BaseModel):
    id: Annotated[int, Field(description="ID del subtema", examples=[1])]
    name: Annotated[
        str,
        Field(
            description="Nombre del subtema",
            examples=["Los Organelos Celulares"],
        ),
    ]
    topic: Annotated[
        TopicSimplePublic,
        Field(description="Tema al que pertenece", examples=["La célula"]),
    ]

    model_config = ConfigDict(from_attributes=True)


class SubtopicPaginatedResponse(BaseModel):
    total_count: Annotated[int, Field(description="Total de subtemas")]
    total_pages: Annotated[int, Field(description="Número de páginas")]
    current_page: Annotated[int, Field(description="Página actual")]
    items_count: Annotated[
        int, Field(description="Total de subtemas de la página actual")
    ]
    has_prev: Annotated[bool, Field(description="Indica si existe una página anterior")]
    has_next: Annotated[
        bool, Field(description="Indica si existe una página siguiente")
    ]
    items: Annotated[
        list[SubtopicPublic],
        Field(description="Lista de preguntas de la página actual"),
    ]

    model_config = ConfigDict(from_attributes=True)
