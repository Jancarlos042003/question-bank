from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class AreaBase(BaseModel):
    name: Annotated[
        str, Field(min_length=1, description="Nombre del área", examples=["Psicología"])
    ]
    code: Annotated[
        str, Field(min_length=2, description="Código del área", examples=["PS"])
    ]


# PRIVADO
class AreaResponse(AreaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# PÚBLICO
class AreaPublic(AreaBase):
    pass


class AreaCodeOnly(BaseModel):
    code: Annotated[str, Field(description="Código del área", examples=["PS"])]
    model_config = ConfigDict(from_attributes=True)
