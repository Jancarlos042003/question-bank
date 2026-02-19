from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.solution_content.schemas import (
    SolutionContentCreateInput,
    SolutionContentPublic,
)


# PRIVADO
class SolutionCreateInput(BaseModel):
    contents: Annotated[
        List[SolutionContentCreateInput],
        Field(min_length=1, description="Contenido de la solución"),
    ]


class SolutionCreate(BaseModel):
    question_id: int


class SolutionUpdateInput(SolutionCreateInput):
    pass


# PÚBLICO
class SolutionPublic(BaseModel):
    id: int
    contents: List[SolutionContentPublic]

    model_config = ConfigDict(from_attributes=True)
