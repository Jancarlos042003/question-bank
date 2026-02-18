from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict

from app.api.v1.source.schemas import SourceSimplePublic


class QuestionSourceCreateInput(BaseModel):
    source_id: Annotated[int, Field(gt=0, description="ID de la fuente", examples=[1])]
    page: Annotated[int, Field(gt=0, description="Página de referencia", examples=[23])]


class QuestionSourcePublic(BaseModel):
    page: Annotated[int, Field(description="Página de referencia", examples=[23])]
    source: Annotated[SourceSimplePublic, Field(description="Fuente asociada")]

    model_config = ConfigDict(from_attributes=True)
