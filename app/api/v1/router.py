from fastapi import APIRouter

from app.api.v1.image.router import image_router
from app.api.v1.institution.router import institution_router
from app.api.v1.question.router import question_router
from app.api.v1.source.router import source_router
from app.api.v1.subtopic.router import subtopic_router
from app.api.v1.topic.router import topic_router

api_v1_router = APIRouter()
api_v1_router.include_router(question_router, prefix="/questions")
api_v1_router.include_router(topic_router, prefix="/topics")
api_v1_router.include_router(subtopic_router, prefix="/subtopics")
api_v1_router.include_router(institution_router, prefix="/institutions")
api_v1_router.include_router(source_router, prefix="/sources")
api_v1_router.include_router(image_router, prefix="/images")
