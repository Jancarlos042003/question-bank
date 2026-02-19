from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.content_type import ContentType


class QuestionContentBase(BaseModel):
    label: Annotated[str | None, Field(default=None, max_length=1, examples=["I"])]
    type: Annotated[
        ContentType,
        Field(
            description="Tipo de contenido",
            examples=[ContentType.TEXT, ContentType.IMAGE],
        ),
    ]
    (
        Field(
            min_length=10,
            examples=["Texto de la pregunta o el path de la imagen"],
        ),
    )
    value: Annotated[
        str,
        Field(min_length=5, examples=["Texto de la pregunta o el path de la imagen"]),
    ]
    order: Annotated[int, Field(description="Orden de aparición", ge=1, examples=[1])]


class QuestionContentCreateInput(QuestionContentBase):
    pass


class QuestionContentCreate(QuestionContentBase):
    question_id: Annotated[int, Field(examples=[10])]


class QuestionContentUpdateInput(BaseModel):
    label: Annotated[str | None, Field(default=None, max_length=1, examples=["I"])]
    type: Annotated[
        ContentType | None,
        Field(
            default=None,
            description="Tipo de contenido",
            examples=[ContentType.TEXT, ContentType.IMAGE],
        ),
    ]
    value: Annotated[
        str | None,
        Field(
            default=None,
            min_length=5,
            examples=["Texto de la pregunta o el path de la imagen"],
        ),
    ]
    order: Annotated[
        int | None,
        Field(default=None, description="Orden de aparición", ge=1, examples=[1]),
    ]

    @model_validator(mode="after")
    def validate_any_field_present(self):
        if (
            self.label is None
            and self.type is None
            and self.value is None
            and self.order is None
        ):
            raise ValueError(
                "Debes enviar al menos un campo para actualizar el contenido."
            )

        return self


class QuestionContentResponse(QuestionContentBase):
    id: Annotated[int, Field(gt=0, examples=[1])]

    model_config = ConfigDict(from_attributes=True)
