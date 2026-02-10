from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DifficultyBase(BaseModel):
    name: Annotated[
        str,
        Field(min_length=1, description="Nombre de la dificultad", examples=["Fácil"]),
    ]
    code: Annotated[str, Field(description="Código de la dificultad", examples=["1"])]


# PRIVADO
class DifficultyCreate(DifficultyBase):
    pass


class DifficultyResponse(DifficultyBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# PÚBLICO
class DifficultyPublic(DifficultyBase):
    pass

    model_config = ConfigDict(from_attributes=True)
