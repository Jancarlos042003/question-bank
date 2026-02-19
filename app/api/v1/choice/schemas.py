from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.api.v1.choice_content.schemas import (
    ChoiceContentCreateInput,
    ChoiceContentPublic,
)


class ChoiceBase(BaseModel):
    label: Annotated[
        str,
        Field(
            max_length=1,
            description="Etiqueta de la opción",
            examples=["A"],
        ),
    ]
    is_correct: Annotated[
        bool,
        Field(description="Indica si la opción es correcta"),
    ]


# PRIVADO
class ChoiceCreateInput(ChoiceBase):
    contents: Annotated[
        List[ChoiceContentCreateInput],
        Field(min_length=1, description="Contenido de la opción"),
    ]


class ChoiceCreate(ChoiceBase):
    question_id: int


class ChoiceUpdateInput(BaseModel):
    label: Annotated[
        str | None,
        Field(
            default=None,
            max_length=1,
            description="Etiqueta de la opción",
            examples=["A"],
        ),
    ]
    is_correct: Annotated[
        bool | None,
        Field(default=None, description="Indica si la opción es correcta"),
    ]
    contents: Annotated[
        List[ChoiceContentCreateInput] | None,
        Field(default=None, min_length=1, description="Contenido de la opción"),
    ]

    @model_validator(mode="after")
    def validate_any_field_present(self):
        if self.label is None and self.is_correct is None and self.contents is None:
            raise ValueError(
                "Debes enviar al menos un campo para actualizar la alternativa."
            )

        return self


# PÚBLICO
class ChoicePublic(BaseModel):
    id: int
    is_correct: bool
    label: Annotated[str, Field(description="Etiqueta de la opción", examples=["A"])]
    contents: List[ChoiceContentPublic]

    model_config = ConfigDict(from_attributes=True)
