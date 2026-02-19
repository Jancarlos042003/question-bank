import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.institution.schemas import InstitutionCreate, InstitutionUpdate
from app.core.exceptions.domain import ResourceNotFoundException, DuplicateValueError
from app.core.exceptions.technical import DeleteError, PersistenceError, RetrievalError
from app.repositories.institution_repository import InstitutionRepository

logger = logging.getLogger(__name__)


class InstitutionService:
    def __init__(self, repository: InstitutionRepository):
        self.repository = repository

    def get_institution(self, institution_id: int):
        try:
            institution = self.repository.get_institution(institution_id)
        except SQLAlchemyError as e:
            logger.exception(f"Error al obtener la institución con ID {institution_id}")
            raise RetrievalError(
                f"Error al obtener la institución con ID {institution_id}"
            ) from e

        if not institution:
            raise ResourceNotFoundException(
                message=f"Institución con ID {institution_id} no encontrada"
            )

        return institution

    def get_institutions(self, page: int, limit: int):
        try:
            return self.repository.get_institutions(page, limit)
        except SQLAlchemyError as e:
            logger.exception(
                f"Error al listar instituciones (page={page}, limit={limit})"
            )
            raise RetrievalError("Error al listar instituciones") from e

    def get_institutions_by_ids(self, ids: list[int]):
        try:
            institutions = self.repository.get_institutions_by_ids(ids)
        except SQLAlchemyError as e:
            logger.exception("Error al obtener instituciones por IDs")
            raise RetrievalError("Error al obtener instituciones") from e

        found_ids = {institution.id for institution in institutions}
        missing_ids = set(ids) - found_ids

        if missing_ids:
            raise ResourceNotFoundException(
                message=f"Instituciones no encontradas para IDs: {missing_ids}"
            )

        return institutions

    def create_institution(self, institution: InstitutionCreate):
        try:
            return self.repository.create_institution(institution)
        except IntegrityError as e:
            logger.exception("IntegrityError al crear institución")

            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23505":
                raise DuplicateValueError("El código de la institución ya existe")

            raise PersistenceError("Error al crear la institución") from e
        except SQLAlchemyError as e:
            logger.exception("Error al crear institución")
            raise PersistenceError("Error al crear la institución") from e

    def update_institution(self, institution_id: int, institution: InstitutionUpdate):
        try:
            updated_institution = self.repository.update_institution(
                institution_id, institution
            )
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar institución")

            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "pgcode", None)

            if pgcode == "23505":
                raise DuplicateValueError("El código de la institución ya existe")

            raise PersistenceError("Error al actualizar la institución") from e
        except SQLAlchemyError as e:
            logger.exception("Error al actualizar institución")
            raise PersistenceError("Error al actualizar la institución") from e

        if not updated_institution:
            raise ResourceNotFoundException(
                message=f"Institución con ID {institution_id} no encontrada"
            )

        return updated_institution

    def delete_institution(self, institution_id: int):
        try:
            institution = self.repository.delete_institution(institution_id)
        except SQLAlchemyError as e:
            logger.exception("Error al eliminar institución con ID %s", institution_id)
            raise DeleteError(
                f"Error al eliminar la institución con ID {institution_id}"
            ) from e

        if not institution:
            raise ResourceNotFoundException(
                message=f"Institución con ID {institution_id} no encontrada"
            )

        return institution
