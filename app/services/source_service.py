import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.source.repository import SourceRepository
from app.api.v1.source.schemas import SourceCreate, SourceUpdate
from app.core.exceptions.domain import ResourceNotFoundException
from app.core.exceptions.technical import DeleteError, PersistenceError, RetrievalError
from app.services.institution_service import InstitutionService

logger = logging.getLogger(__name__)


class SourceService:
    def __init__(
        self,
        repository: SourceRepository,
        institution_service: InstitutionService | None = None,
    ):
        self.repository = repository
        self.institution_service = institution_service

    def get_source(self, source_id: int):
        try:
            source = self.repository.get_source(source_id)
        except SQLAlchemyError as e:
            logger.exception(f"Error al obtener la fuente con ID {source_id}")
            raise RetrievalError(f"Error al obtener la fuente con ID {source_id}") from e

        if not source:
            raise ResourceNotFoundException(
                message=f"Fuente con ID {source_id} no encontrada"
            )

        return source

    def get_sources(self, page: int, limit: int):
        try:
            return self.repository.get_sources(page, limit)
        except SQLAlchemyError as e:
            logger.exception(f"Error al listar fuentes (page={page}, limit={limit})")
            raise RetrievalError("Error al listar fuentes") from e

    def get_sources_by_ids(self, ids: list[int]):
        try:
            sources = self.repository.get_sources_by_ids(ids)
        except SQLAlchemyError as e:
            logger.exception("Error al obtener fuentes por IDs")
            raise RetrievalError("Error al obtener fuentes") from e

        found_ids = {source.id for source in sources}
        missing_ids = set(ids) - found_ids

        if missing_ids:
            raise ResourceNotFoundException(
                message=f"Fuentes no encontradas para IDs: {missing_ids}"
            )

        return sources

    def create_source(self, source: SourceCreate):
        self.institution_service.get_institution(source.institution_id)

        try:
            return self.repository.create_source(source)
        except IntegrityError as e:
            logger.exception("IntegrityError al crear fuente")
            raise PersistenceError("Error al crear la fuente") from e
        except SQLAlchemyError as e:
            logger.exception("Error al crear fuente")
            raise PersistenceError("Error al crear la fuente") from e

    def update_source(self, source_id: int, source: SourceUpdate):
        if source.institution_id is not None:
            self.institution_service.get_institution(source.institution_id)

        try:
            updated_source = self.repository.update_source(source_id, source)
        except IntegrityError as e:
            logger.exception("IntegrityError al actualizar fuente")
            raise PersistenceError("Error al actualizar la fuente") from e
        except SQLAlchemyError as e:
            logger.exception("Error al actualizar fuente")
            raise PersistenceError("Error al actualizar la fuente") from e

        if not updated_source:
            raise ResourceNotFoundException(message=f"Fuente con ID {source_id} no encontrada")

        return updated_source

    def delete_source(self, source_id: int):
        try:
            source = self.repository.delete_source(source_id)
        except SQLAlchemyError as e:
            logger.exception("Error al eliminar fuente con ID %s", source_id)
            raise DeleteError(f"Error al eliminar la fuente con ID {source_id}") from e

        if not source:
            raise ResourceNotFoundException(message=f"Fuente con ID {source_id} no encontrada")

        return source
