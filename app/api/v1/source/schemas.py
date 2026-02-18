from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.institution.schemas import InstitutionSimplePublic


class SourceBase(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=1,
            description="Nombre de la fuente",
            examples=["Examen de Admisión UNMSM"],
        ),
    ]
    year: Annotated[
        int,
        Field(ge=1900, le=2100, description="Año de la fuente", examples=[2025]),
    ]


class SourceCreate(SourceBase):
    institution_id: Annotated[
        int,
        Field(gt=0, description="ID de la institución", examples=[1]),
    ]


class SourceUpdate(BaseModel):
    name: Annotated[
        str | None,
        Field(
            default=None,
            min_length=1,
            description="Nombre de la fuente",
            examples=["Examen de Admisión UNMSM"],
        ),
    ]
    year: Annotated[
        int | None,
        Field(
            default=None,
            ge=1900,
            le=2100,
            description="Año de la fuente",
            examples=[2025],
        ),
    ]
    institution_id: Annotated[
        int | None,
        Field(default=None, gt=0, description="ID de la institución", examples=[1]),
    ]


class SourcePublic(SourceBase):
    id: Annotated[int, Field(description="ID de la fuente", examples=[1])]
    institution: Annotated[
        InstitutionSimplePublic,
        Field(description="Institución a la que pertenece la fuente"),
    ]

    model_config = ConfigDict(from_attributes=True)


class SourceSimplePublic(BaseModel):
    id: Annotated[int, Field(description="ID de la fuente", examples=[1])]
    name: Annotated[
        str,
        Field(description="Nombre de la fuente", examples=["Examen de Admisión UNI"]),
    ]
    year: Annotated[int, Field(description="Año de la fuente", examples=[2025])]

    model_config = ConfigDict(from_attributes=True)


class SourcePaginatedResponse(BaseModel):
    total_count: Annotated[int, Field(description="Total de fuentes")]
    total_pages: Annotated[int, Field(description="Número de páginas")]
    current_page: Annotated[int, Field(description="Página actual")]
    items_count: Annotated[
        int, Field(description="Total de fuentes de la página actual")
    ]
    has_prev: Annotated[bool, Field(description="Indica si existe una página anterior")]
    has_next: Annotated[
        bool, Field(description="Indica si existe una página siguiente")
    ]
    items: Annotated[
        list[SourcePublic],
        Field(description="Lista de fuentes de la página actual"),
    ]

    model_config = ConfigDict(from_attributes=True)
