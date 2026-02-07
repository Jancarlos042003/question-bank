from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.solution_content.shemas import (
    SolutionContentCreateInput,
    SolutionContentResponse,
)


class SolutionCreateInput(BaseModel):
    contents: Annotated[
        List[SolutionContentCreateInput], Field(description="Contenido de la solución")
    ]


class SolutionCreate(BaseModel):
    question_id: int


class SolutionResponse(BaseModel):
    id: int
    contents: List[SolutionContentResponse]

    model_config = ConfigDict(from_attributes=True)
