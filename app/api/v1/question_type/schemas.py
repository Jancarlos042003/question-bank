from pydantic import BaseModel, ConfigDict


class QuestionTypeBase(BaseModel):
    name: str
    code: str


class QuestionTypeRead(QuestionTypeBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )
