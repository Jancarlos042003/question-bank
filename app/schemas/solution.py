from pydantic import BaseModel, Field
from typing import Annotated, List


class SolutionBase(BaseModel):
    explanation: Annotated[
        str, Field(description="Explicación detallada de la solución")
    ]


class SolutionCreate(SolutionBase):
    pass


class SolutionRead(SolutionBase):
    image_paths: List[str] | None = None
