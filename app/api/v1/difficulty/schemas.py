from pydantic import BaseModel, ConfigDict


class DifficultyBase(BaseModel):
    name: str
    code: str


class DifficultyCreate(DifficultyBase):
    pass


class DifficultyResponse(DifficultyBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
