from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.v1.institution.repository import InstitutionRepository
from app.api.v1.source.repository import SourceRepository
from app.api.v1.source.schemas import (
    SourceCreate,
    SourcePaginatedResponse,
    SourcePublic,
    SourceUpdate,
)
from app.db.session import get_session
from app.services.institution_service import InstitutionService
from app.services.source_service import SourceService

source_router = APIRouter(tags=["Source"])


def get_institution_service(db: Annotated[Session, Depends(get_session)]):
    institution_repository = InstitutionRepository(db)
    return InstitutionService(institution_repository)


def get_source_service(
    db: Annotated[Session, Depends(get_session)],
    institution_service: Annotated[InstitutionService, Depends(get_institution_service)],
):
    source_repository = SourceRepository(db)
    return SourceService(source_repository, institution_service)


@source_router.post(
    "",
    response_model=SourcePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una fuente",
)
def add_source(
    service: Annotated[SourceService, Depends(get_source_service)],
    source: SourceCreate,
):
    return service.create_source(source)


@source_router.get("", response_model=SourcePaginatedResponse, summary="Listar fuentes")
def read_sources(
    service: Annotated[SourceService, Depends(get_source_service)],
    page: Annotated[int, Query(ge=1, description="Número de página")] = 1,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Cantidad de elementos por página")
    ] = 50,
):
    return service.get_sources(page, limit)


@source_router.get(
    "/{source_id}",
    response_model=SourcePublic,
    summary="Obtener una fuente por ID",
)
def read_source(
    service: Annotated[SourceService, Depends(get_source_service)],
    source_id: Annotated[int, Path(ge=1, description="ID de la fuente")],
):
    return service.get_source(source_id)


@source_router.patch(
    "/{source_id}",
    response_model=SourcePublic,
    summary="Actualizar una fuente",
)
def update_source(
    service: Annotated[SourceService, Depends(get_source_service)],
    source_id: Annotated[int, Path(ge=1, description="ID de la fuente")],
    source: SourceUpdate,
):
    return service.update_source(source_id, source)


@source_router.delete(
    "/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una fuente",
)
def delete_source(
    service: Annotated[SourceService, Depends(get_source_service)],
    source_id: Annotated[int, Path(ge=1, description="ID de la fuente")],
):
    return service.delete_source(source_id)
