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
    def __init__(self, storage: StoragePort, storage_container_name: str):
        self.storage = storage
        self.storage_container_name = storage_container_name

    async def upload_image(self, image: UploadFile, destination: str) -> str:
        allowed_content_types = {"image/jpeg", "image/png", "image/webp"}

        # Verificar el tipo de contenido
        if image.content_type not in allowed_content_types:
            raise ContentTypeError(
                f"Tipo de contenido no válido: '{image.content_type}'"
            )

        image_bytes = await image.read()

        try:
            image_path = self.storage.upload_object_from_bytes(
                storage_container_name=self.storage_container_name,
                data=image_bytes,
                destination=destination,
                content_type=image.content_type,
            )
        except NotFound as e:
            logger.exception("El bucket '%s' no existe", self.storage_container_name)
            raise StorageBucketNotFoundError("El bucket no existe") from e
        except Forbidden as e:
            logger.exception(
                "Permisos insuficientes para subir al bucket '%s'",
                self.storage_container_name,
            )
            raise StoragePermissionDeniedError(
                "Permisos insuficientes para subir el archivo"
            ) from e
        except BadRequest as e:
            logger.exception("Error en la solicitud: %s", e.message)
            raise StorageError("Solicitud inválida al subir archivo") from e
        except GoogleAPIError as e:
            logger.exception("Error de Google Cloud Storage: %s", e)
            raise StorageError("Error en el servicio de almacenamiento") from e
        except Exception as e:
            logger.exception("Error inesperado al subir archivo: %s", e)
            raise StorageError("Error inesperado en almacenamiento") from e
        else:
            return image_path

    def generate_signature(self, storage_object_name: str):
        try:
            url = self.storage.generate_signed_url(
                storage_container_name=self.storage_container_name,
                storage_object_name=storage_object_name,
            )
        except Forbidden:
            logger.error("Permisos insuficientes para generar URL firmada")
            raise StoragePermissionDeniedError(
                "Permisos insuficientes para generar URL firmada"
            )
        except BadRequest as e:
            logger.exception("Parámetros inválidos al generar la URL: %s", e.message)
            raise StorageError("Parámetros inválidos al generar la URL") from e
        except GoogleAPIError as e:
            logger.exception("Error de Google Cloud Storage: %s", e)
            raise StorageError("Error en el servicio de almacenamiento") from e
        except Exception as e:
            logger.exception("Error inesperado al generar la URL firmada: %s", e)
            raise StorageError("Error inesperado al generar la URL firmada") from e
        else:
            return url
