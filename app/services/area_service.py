import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.domain import ResourceNotFoundException
from app.core.exceptions.technical import RetrievalError
from app.repositories.area_repository import AreaRepository

logger = logging.getLogger(__name__)


class AreaService:
    def __init__(self, area_repository: AreaRepository):
        self.area_repository = area_repository

    def get_areas(self, ids: list[int]):
        try:
            areas = self.area_repository.get_areas(ids)
        except SQLAlchemyError as e:
            logger.exception(f"Error al obtener áreas")
            raise RetrievalError("Error al obtener áreas") from e

        # Obtener los ID's encontrados
        found_ids = {area.id for area in areas}

        # Obtener los ID's faltantes
        missing_ids = set(ids) - found_ids  # Convertimos las lista de ids en un set

        if missing_ids:
            raise ResourceNotFoundException(f"IDs not found: {missing_ids}")

        return areas
