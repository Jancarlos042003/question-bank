from pydantic import BaseModel


class SubtopicBase(BaseModel):
    name: str


class SubtopicCreate(SubtopicBase):
    topic_id: int


class SubtopicRead(SubtopicBase):
    id: int


class SubtopicUpdate(SubtopicBase):
    pass
