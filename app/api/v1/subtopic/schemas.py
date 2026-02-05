from pydantic import BaseModel

from app.api.v1.topic.schemas import TopicSimpleResponse


class SubtopicBase(BaseModel):
    name: str


class SubtopicCreate(SubtopicBase):
    topic_id: int


class SubtopicResponse(SubtopicBase):
    id: int
    topic: TopicSimpleResponse


class SubtopicUpdate(SubtopicBase):
    pass
