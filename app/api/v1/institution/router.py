from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.v1.institution.schemas import (
    InstitutionCreate,
    InstitutionPaginatedResponse,
    InstitutionPublic,
    InstitutionUpdate,
)
from app.db.session import get_session
from app.repositories.institution_repository import InstitutionRepository
from app.services.institution_service import InstitutionService

institution_router = APIRouter(tags=["Institution"])


def get_institution_service(db: Annotated[Session, Depends(get_session)]):
    institution_repository = InstitutionRepository(db)
    return InstitutionService(institution_repository)


@institution_router.post(
    "",
    response_model=InstitutionPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una institución",
)
def add_institution(
        service: Annotated[InstitutionService, Depends(get_institution_service)],
        institution: InstitutionCreate,
):
    return service.create_institution(institution)


@institution_router.get(
    "", response_model=InstitutionPaginatedResponse, summary="Listar instituciones"
)
def read_institutions(
        service: Annotated[InstitutionService, Depends(get_institution_service)],
        page: Annotated[int, Query(ge=1, description="Número de página")] = 1,
        limit: Annotated[
            int, Query(ge=1, le=100, description="Cantidad de elementos por página")
        ] = 50,
):
    """Recupera instituciones de la base de datos con soporte para paginación."""
    return service.get_institutions(page, limit)


@institution_router.get(
    "/{institution_id}",
    response_model=InstitutionPublic,
    summary="Obtener una institución por ID",
)
def read_institution(
        service: Annotated[InstitutionService, Depends(get_institution_service)],
        institution_id: Annotated[int, Path(ge=1, description="ID de la institución")],
):
    return service.get_institution(institution_id)


@institution_router.patch(
    "/{institution_id}",
    response_model=InstitutionPublic,
    summary="Actualizar una institución",
)
def update_institution(
        service: Annotated[InstitutionService, Depends(get_institution_service)],
        institution_id: Annotated[int, Path(ge=1, description="ID de la institución")],
        institution: InstitutionUpdate,
):
    return service.update_institution(institution_id, institution)


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
