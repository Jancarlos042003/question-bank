from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field

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


# PÚBLICO
class ChoicePublic(BaseModel):
    is_correct: bool
    label: Annotated[str, Field(description="Etiqueta de la opción", examples=["A"])]
    contents: List[ChoiceContentPublic]

    model_config = ConfigDict(from_attributes=True)
