from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_session
from app.infrastructure.gcp.storage_adapter import GCPStorageAdapter
from app.ports.storage_port import StoragePort
from app.repositories.area_repository import AreaRepository
from app.repositories.choice_repository import ChoiceRepository
from app.repositories.institution_repository import InstitutionRepository
from app.repositories.question_content_repository import QuestionContentRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.question_source_repository import QuestionSourceRepository
from app.repositories.solution_repository import SolutionRepository
from app.repositories.source_repository import SourceRepository
from app.services.area_service import AreaService
from app.services.choice_service import ChoiceService
from app.services.image_service import ImageService
from app.services.institution_service import InstitutionService
from app.services.question_content_service import QuestionContentService
from app.services.question_guard_service import QuestionGuardService
from app.services.question_service import QuestionService
from app.services.question_source_service import QuestionSourceService
from app.services.solution_service import SolutionService
from app.services.source_service import SourceService


def get_area_service(db: Annotated[Session, Depends(get_session)]):
    area_repository = AreaRepository(db)
    return AreaService(area_repository)


def get_gcp_storage():
    return GCPStorageAdapter()


def get_institution_service(db: Annotated[Session, Depends(get_session)]):
    institution_repository = InstitutionRepository(db)
    return InstitutionService(institution_repository)


def get_source_service(
    db: Annotated[Session, Depends(get_session)],
    institution_service: Annotated[
        InstitutionService, Depends(get_institution_service)
    ],
):
    source_repository = SourceRepository(db)
    return SourceService(source_repository, institution_service)


def get_image_service(storage: Annotated[StoragePort, Depends(get_gcp_storage)]):
    return ImageService(storage, settings.CONTAINER_NAME)


def get_question_service(
    db: Annotated[Session, Depends(get_session)],
    area_service: Annotated[AreaService, Depends(get_area_service)],
    source_service: Annotated[SourceService, Depends(get_source_service)],
    image_service: Annotated[ImageService, Depends(get_image_service)],
) -> QuestionService:
    question_repository = QuestionRepository(db)
    return QuestionService(
        question_repository, area_service, source_service, image_service
    )


def get_question_guard_service(
    db: Annotated[Session, Depends(get_session)],
) -> QuestionGuardService:
    question_repository = QuestionRepository(db)
    return QuestionGuardService(question_repository)


def get_choice_service(
    db: Annotated[Session, Depends(get_session)],
    image_service: Annotated[ImageService, Depends(get_image_service)],
    question_guard_service: Annotated[
        QuestionGuardService, Depends(get_question_guard_service)
    ],
) -> ChoiceService:
    choice_repository = ChoiceRepository(db)
    return ChoiceService(choice_repository, image_service, question_guard_service)


def get_solution_service(
    db: Annotated[Session, Depends(get_session)],
    image_service: Annotated[ImageService, Depends(get_image_service)],
    question_guard_service: Annotated[
        QuestionGuardService, Depends(get_question_guard_service)
    ],
) -> SolutionService:
    solution_repository = SolutionRepository(db)
    return SolutionService(solution_repository, image_service, question_guard_service)


def get_question_content_service(
    db: Annotated[Session, Depends(get_session)],
    image_service: Annotated[ImageService, Depends(get_image_service)],
    question_guard_service: Annotated[
        QuestionGuardService, Depends(get_question_guard_service)
    ],
) -> QuestionContentService:
    question_content_repository = QuestionContentRepository(db)
    return QuestionContentService(
        question_content_repository, image_service, question_guard_service
    )


def get_question_source_service(
    db: Annotated[Session, Depends(get_session)],
    source_service: Annotated[SourceService, Depends(get_source_service)],
    question_guard_service: Annotated[
        QuestionGuardService, Depends(get_question_guard_service)
    ],
) -> QuestionSourceService:
    question_source_repository = QuestionSourceRepository(db)
    return QuestionSourceService(
        question_source_repository, source_service, question_guard_service
    )
