from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.v1.source.schemas import (
    SourceCreate,
    SourcePublic,
    SourceUpdate,
)
from app.db.session import get_session
from app.helpers.build_paginated import build_paginated_response
from app.schemas.pagination import PaginationMeta
from app.schemas.response import ApiResponse
from app.repositories.institution_repository import InstitutionRepository
from app.repositories.source_repository import SourceRepository
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
    response_model=ApiResponse[SourcePublic],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una fuente",
)
def add_source(
    service: Annotated[SourceService, Depends(get_source_service)],
    source: SourceCreate,
):
    created_source = service.create_source(source)
    return {"data": created_source}


@source_router.get(
    "",
    response_model=ApiResponse[list[SourcePublic], PaginationMeta],
    summary="Listar fuentes",
)
def read_sources(
    service: Annotated[SourceService, Depends(get_source_service)],
    page: Annotated[int, Query(ge=1, description="Número de página")] = 1,
    limit: Annotated[
    int, Query(ge=1, le=100, description="Cantidad de elementos por página")
    ] = 50,
):
    items, total = service.get_sources(page, limit)
    return build_paginated_response(items=items, total=total, page=page, limit=limit)


@source_router.get(
    "/{source_id}",
    response_model=ApiResponse[SourcePublic],
    summary="Obtener una fuente por ID",
)
def read_source(
    service: Annotated[SourceService, Depends(get_source_service)],
    source_id: Annotated[int, Path(ge=1, description="ID de la fuente")],
):
    source = service.get_source(source_id)
    return {"data": source}


@source_router.patch(
    "/{source_id}",
    response_model=ApiResponse[SourcePublic],
    summary="Actualizar una fuente",
)
def update_source(
    service: Annotated[SourceService, Depends(get_source_service)],
    source_id: Annotated[int, Path(ge=1, description="ID de la fuente")],
    source: SourceUpdate,
):
    updated_source = service.update_source(source_id, source)
    return {"data": updated_source}


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
