from pydantic import BaseModel


class TopicBase(BaseModel):
    name: str
    description: str


class TopicCreate(TopicBase):
    course_id: int


class TopicRead(TopicBase):
    id: int


class TopicUpdate(TopicBase):
    pass
