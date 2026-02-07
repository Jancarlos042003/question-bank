from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.choice_content.schemas import (
    ChoiceContentCreateInput,
    ChoiceContentResponse,
)


class ChoiceBase(BaseModel):
    label: Annotated[str, Field(max_length=1, examples=["A, B, C, D, E"])]
    is_correct: Annotated[
        bool,
        Field(description="Indica si la opción es correcta"),
    ]


class ChoiceCreateInput(ChoiceBase):
    contents: Annotated[
        List[ChoiceContentCreateInput],
        Field(min_length=1, description="Contenido de la opción"),
    ]


class ChoiceCreate(ChoiceBase):
    question_id: int


class ChoiceResponse(BaseModel):
    is_correct: bool
    contents: List[ChoiceContentResponse]

    model_config = ConfigDict(from_attributes=True)
