from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class TopicUpdate(TopicBase):
    pass
