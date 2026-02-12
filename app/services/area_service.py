from app.api.v1.area.repository import AreaRepository
from app.core.exceptions.domain import ResourceNotFoundException


class AreaService:
    def __init__(self, area_repository: AreaRepository):
        self.area_repository = area_repository

    def get_areas(self, ids: list[int]):
        areas = self.area_repository.get_areas(ids)

        found_ids = {area.id for area in areas}

        # Obtener los ID's faltantes
        missing_ids = set(ids) - found_ids  # Convertimos las lista de ids en un set

        if missing_ids:
            raise ResourceNotFoundException(f"IDs not found: {missing_ids}")

        return areas
