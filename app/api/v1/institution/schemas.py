from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class InstitutionType(StrEnum):
    UNIVERSITY = "universidad"
    EDITORIAL = "editorial"
    ACADEMY = "academia"
    OTHER = "otro"


class InstitutionBase(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=1,
            description="Nombre de la institución",
            examples=["Universidad Nacional Mayor de San Marcos"],
        ),
    ]
    code: Annotated[
        str,
        Field(
            min_length=1,
            max_length=10,
            description="Código de institución",
            examples=["UNMSM"],
        ),
    ]
    type: Annotated[
        InstitutionType,
        Field(description="Tipo de institución", examples=[InstitutionType.UNIVERSITY]),
    ]


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionUpdate(BaseModel):
    name: Annotated[
        str | None,
        Field(default=None, min_length=1, description="Nombre de la institución"),
    ]
    code: Annotated[
        str | None,
        Field(
            default=None,
            min_length=1,
            max_length=10,
            description="Código de institución",
        ),
    ]
    type: Annotated[
        InstitutionType | None,
        Field(default=None, description="Tipo de institución"),
    ]


class InstitutionPublic(InstitutionBase):
    id: Annotated[int, Field(description="ID de la institución", examples=[1])]

    model_config = ConfigDict(from_attributes=True)


class InstitutionSimplePublic(BaseModel):
    id: Annotated[int, Field(description="ID de la institución", examples=[1])]
    name: Annotated[
        str,
        Field(
            description="Nombre de la institución",
            examples=["Universidad Nacional de Ingeniería"],
        ),
    ]
    code: Annotated[str, Field(description="Código de institución", examples=["UNI"])]

    model_config = ConfigDict(from_attributes=True)


class InstitutionPaginatedResponse(BaseModel):
    total_count: Annotated[int, Field(description="Total de instituciones")]
    total_pages: Annotated[int, Field(description="Número de páginas")]
    current_page: Annotated[int, Field(description="Página actual")]
    items_count: Annotated[
        int, Field(description="Total de instituciones de la página actual")
    ]
    has_prev: Annotated[bool, Field(description="Indica si existe una página anterior")]
    has_next: Annotated[
        bool, Field(description="Indica si existe una página siguiente")
    ]
    items: Annotated[
        list[InstitutionPublic],
        Field(description="Lista de instituciones de la página actual"),
    ]

    model_config = ConfigDict(from_attributes=True)
