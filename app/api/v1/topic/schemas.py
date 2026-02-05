from pydantic import BaseModel


class TopicBase(BaseModel):
    name: str
    description: str


class TopicCreate(TopicBase):
    course_id: int


class TopicResponse(TopicBase):
    id: int


class TopicSimpleResponse(BaseModel):
    id: int
    name: str


class TopicUpdate(TopicBase):
    pass
