from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.domain.content_type import ContentType


class ChoiceContentBase(BaseModel):
    type: Annotated[
        ContentType,
        Field(
            description="Tipo de contenido",
            examples=[ContentType.TEXT, ContentType.IMAGE],
        ),
    ]
    value: Annotated[
        str,
        Field(
            min_length=1,
            examples=["Texto de la opción o el path de la imagen"],
        ),
    ]
    order: Annotated[int, Field(description="Orden de aparición", ge=1, examples=[1])]


# PRIVADO
class ChoiceContentCreateInput(ChoiceContentBase):
    pass


class ChoiceContentCreate(ChoiceContentBase):
    choice_id: int


# PÚBLICO
class ChoiceContentPublic(ChoiceContentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
