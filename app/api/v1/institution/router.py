from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.v1.institution.schemas import (
    InstitutionCreate,
    InstitutionPublic,
    InstitutionUpdate,
)
from app.db.session import get_session
from app.helpers.build_paginated import build_paginated_response
from app.schemas.pagination import PaginationMeta
from app.schemas.response import ApiResponse
from app.repositories.institution_repository import InstitutionRepository
from app.services.institution_service import InstitutionService

institution_router = APIRouter(tags=["Institution"])


def get_institution_service(db: Annotated[Session, Depends(get_session)]):
    institution_repository = InstitutionRepository(db)
    return InstitutionService(institution_repository)


@institution_router.post(
    "",
    response_model=ApiResponse[InstitutionPublic],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una institución",
)
def add_institution(
        service: Annotated[InstitutionService, Depends(get_institution_service)],
        institution: InstitutionCreate,
):
    created_institution = service.create_institution(institution)
    return {"data": created_institution}


@institution_router.get(
    "",
    response_model=ApiResponse[list[InstitutionPublic], PaginationMeta],
    summary="Listar instituciones",
)
def read_institutions(
        service: Annotated[InstitutionService, Depends(get_institution_service)],
        page: Annotated[int, Query(ge=1, description="Número de página")] = 1,
        limit: Annotated[
            int, Query(ge=1, le=100, description="Cantidad de elementos por página")
        ] = 50,
):
    """Recupera instituciones de la base de datos con soporte para paginación."""
    items, total = service.get_institutions(page, limit)
    return build_paginated_response(items=items, total=total, page=page, limit=limit)


@institution_router.get(
    "/{institution_id}",
    response_model=ApiResponse[InstitutionPublic],
    summary="Obtener una institución por ID",
)
def read_institution(
        service: Annotated[InstitutionService, Depends(get_institution_service)],
        institution_id: Annotated[int, Path(ge=1, description="ID de la institución")],
):
    institution = service.get_institution(institution_id)
    return {"data": institution}


@institution_router.patch(
    "/{institution_id}",
    response_model=ApiResponse[InstitutionPublic],
    summary="Actualizar una institución",
)
def update_institution(
        service: Annotated[InstitutionService, Depends(get_institution_service)],
        institution_id: Annotated[int, Path(ge=1, description="ID de la institución")],
        institution: InstitutionUpdate,
):
    updated_institution = service.update_institution(institution_id, institution)
    return {"data": updated_institution}


@institution_router.delete(
    "/{institution_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una institución",
)
def delete_institution(
        service: Annotated[InstitutionService, Depends(get_institution_service)],
        institution_id: Annotated[int, Path(ge=1, description="ID de la institución")],
):
    return service.delete_institution(institution_id)
