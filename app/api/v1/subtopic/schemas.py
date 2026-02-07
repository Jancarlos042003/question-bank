from pydantic import BaseModel, ConfigDict

from app.api.v1.topic.schemas import TopicSimpleResponse


class SubtopicBase(BaseModel):
    name: str


class SubtopicCreate(SubtopicBase):
    topic_id: int


class SubtopicResponse(SubtopicBase):
    id: int
    name: str
    topic: TopicSimpleResponse

    model_config = ConfigDict(from_attributes=True)


class SubtopicUpdate(SubtopicBase):
    pass
