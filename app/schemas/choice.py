from typing import Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict


class ChoiceBase(BaseModel):
    label: Annotated[str, Field(..., max_length=1, examples=["A"])]
    content: str
    image_url: Optional[str] = None


class ChoiceCreate(ChoiceBase):
    is_correct: bool
    question_id: int


class ChoiceRead(ChoiceBase):
    id: int
    is_correct: bool
    question_id: int

    model_config = ConfigDict(
        from_attributes=True
    )
