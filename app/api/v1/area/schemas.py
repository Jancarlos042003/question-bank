from pydantic import BaseModel, ConfigDict


class AreaBase(BaseModel):
    name: str
    code: str


class AreaResponse(AreaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
