import logging

from fastapi import UploadFile
from google.api_core.exceptions import (
    BadRequest,
    Forbidden,
    NotFound,
    GoogleAPIError,
)

from app.core.exceptions.domain import ContentTypeError
from app.core.exceptions.technical import (
    StorageBucketNotFoundError,
    StoragePermissionDeniedError,
    StorageError,
)
from app.ports.storage_port import StoragePort

logger = logging.getLogger(__name__)


class ImageService:
    def __init__(self, storage: StoragePort):
        self.storage = storage

    async def upload_image(
            self, image: UploadFile, storage_container_name: str, destination: str
    ) -> str:
        allowed_content_types = {"image/jpeg", "image/png", "image/webp"}

        # Verificar el tipo de contenido
        if image.content_type not in allowed_content_types:
            raise ContentTypeError(
                f"Tipo de contenido no válido: '{image.content_type}'"
            )

        image_bytes = await image.read()

        try:
            image_path = self.storage.upload_object_from_bytes(
                storage_container_name=storage_container_name,
                data=image_bytes,
                destination=destination,
                content_type=image.content_type,
            )
        except NotFound:
            logger.error("El bucket '%s' no existe", storage_container_name)
            raise StorageBucketNotFoundError("El bucket no existe")
        except Forbidden:
            logger.error(
                "Permisos insuficientes para subir al bucket '%s'",
                storage_container_name,
            )
            raise StoragePermissionDeniedError(
                "Permisos insuficientes para subir el archivo"
            )
        except BadRequest as e:
            logger.error("Error en la solicitud: %s", e.message)
            raise StorageError("Solicitud inválida al subir archivo")
        except GoogleAPIError as e:
            logger.error("Error de Google Cloud Storage: %s", e, exc_info=True)
            raise StorageError("Error en el servicio de almacenamiento")
        except Exception as e:
            logger.error("Error inesperado al subir archivo: %s", e, exc_info=True)
            raise StorageError("Error inesperado en almacenamiento")
        else:
            return image_path

    def generate_signature(self, storage_container_name: str, storage_object_name: str):
        try:
            url = self.storage.generate_signed_url(
                storage_container_name=storage_container_name,
                storage_object_name=storage_object_name,
            )
        except Forbidden:
            logger.error("Permisos insuficientes para generar URL firmada")
            raise StoragePermissionDeniedError(
                "Permisos insuficientes para generar URL firmada"
            )
        except BadRequest as e:
            logger.error("Parámetros inválidos al generar la URL: %s", e.message)
            raise StorageError("Parámetros inválidos al generar la URL")
        except GoogleAPIError as e:
            logger.error("Error de Google Cloud Storage: %s", e, exc_info=True)
            raise StorageError("Error en el servicio de almacenamiento")
        except Exception as e:
            logger.error(
                "Error inesperado al generar la URL firmada: %s", e, exc_info=True
            )
            raise StorageError("Error inesperado al generar la URL firmada")
        else:
            return url
