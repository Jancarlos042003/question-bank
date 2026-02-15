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
    return ImageService(storage, settings.CONTAINER_NAME)


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
        image=image, destination=f"unmsm/courses/{course}/{directory}/{image.filename}"
    )
