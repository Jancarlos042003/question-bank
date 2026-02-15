from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Depends, Query

from app.core.config import settings
from app.infrastructure.gcp.storage_adapter import GCPStorageAdapter
from app.ports.storage_port import StoragePort
from app.services.image_service import ImageService

image_router = APIRouter(tags=["Image"])


# DEPENDENCIAS
def get_gcp_storage() -> StoragePort:
    return GCPStorageAdapter()


def get_image_service(storage: Annotated[StoragePort, Depends(get_gcp_storage)]):
    return ImageService(storage)


@image_router.post("", summary="Subir imagen")
async def upload_image(
        image: Annotated[UploadFile, File(description="Imagen a subir")],
        service: Annotated[ImageService, Depends(get_image_service)],
        course: Annotated[str, Query(description="Nombre del curso")],
        directory: Annotated[
            str,
            Query(
                description="Carpeta destino de almacenamiento (statements / choices / solutions)"
            ),
        ],
):
    return await service.upload_image(
        image=image,
        storage_container_name=settings.CONTAINER_NAME,
        # En GCS, no existen las carpetas reales, solo objetos con nombres largos.
        # TODO manejar el caso donde existen nombres repetidos
        destination=f"unmsm/courses/{course}/{directory}/{image.filename}",
    )
