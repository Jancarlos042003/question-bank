from pydantic import BaseModel


class AreaBase(BaseModel):
    name: str
    code: str


class AreaResponse(AreaBase):
    id: int
