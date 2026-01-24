from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class ChoiceBase(BaseModel):
    label: Annotated[
        str,
        Field(max_length=1, description="Etiqueta única de la opción", examples=["A"]),
    ]
    content: Annotated[
        str | None,
        Field(
            default=None,
            description="Texto de la opción",
            examples=["Opción de ejemplo"],
        ),
    ]


class ChoiceCreate(ChoiceBase):
    is_correct: Annotated[
        bool, Field(description="Indica si la opción es correcta", examples=[True])
    ]


class ChoiceRead(ChoiceBase):
    id: int
    is_correct: bool
    question_id: int
    image_path: str | None = None

    model_config = ConfigDict(from_attributes=True)
