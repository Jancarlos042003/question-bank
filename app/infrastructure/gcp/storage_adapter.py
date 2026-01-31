import datetime
import logging

from google.api_core.exceptions import (
    BadRequest,
    Forbidden,
    GoogleAPIError,
    NotFound,
)
from google.cloud.storage import Client

from app.core.config import settings
from app.ports.storage_port import StoragePort


# https://docs.cloud.google.com/python/docs/reference/storage/latest
class GCPStorageAdapter(StoragePort):
    def __init__(self):
        # DEV
        if (
            hasattr(settings, "GOOGLE_APPLICATION_CREDENTIALS")
            and settings.GOOGLE_APPLICATION_CREDENTIALS
        ):
            self.storage_client = Client.from_service_account_json(
                settings.GOOGLE_APPLICATION_CREDENTIALS
            )
        # PROD
        else:
            self.storage_client = Client()

    # https://docs.cloud.google.com/storage/docs/access-control/signing-urls-manually?hl=es-419
    def generate_signed_url(
        self, storage_container_name: str, storage_object_name: str
    ) -> str:
        try:
            bucket = self.storage_client.bucket(storage_container_name)
            blob = bucket.blob(storage_object_name)

            if not blob.exists():
                raise FileNotFoundError(
                    f"El objeto '{storage_object_name}' no existe en el bucket '{storage_container_name}'"
                )

            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=15),
                # content_type="image/webp",
                method="GET",
            )

            return url
        except FileNotFoundError as e:
            logging.warning("❌ %s", str(e))
            raise
        except Forbidden:
            logging.error("❌ Permisos insuficientes para generar URL firmada")
            raise
        except BadRequest as e:
            logging.error("❌ Parámetros inválidos al generar la URL: %s", e.message)
            raise
        except GoogleAPIError as e:
            logging.error("❌ Error de Google Cloud Storage: %s", str(e))
            raise
        except Exception:
            logging.exception("❌ Error inesperado al generar la URL firmada")
            raise

    # https://docs.cloud.google.com/storage/docs/uploading-objects-from-memory?hl=es-419#uploading-an-object-from-memory
    def upload_object_from_bytes(
        self,
        storage_container_name: str,
        data: bytes,
        destination: str,
        content_type: str | None = None,
    ):
        try:
            bucket = self.storage_client.bucket(storage_container_name)
            blob = bucket.blob(destination)

            blob.upload_from_string(data, content_type=content_type)

            return destination[1:]
        except NotFound:
            logging.error("❌ El bucket '%s' no existe", storage_container_name)
            raise
        except Forbidden:
            logging.error(
                "❌ Permisos insuficientes para subir al bucket '%s'",
                storage_container_name,
            )
            raise
        except BadRequest as e:
            logging.error("❌ Error en la solicitud: %s", e.message)
            raise
        except GoogleAPIError as e:
            logging.error("❌ Error de Google Cloud Storage: %s", str(e))
            raise
        except Exception:
            logging.exception("❌ Error inesperado al subir archivo")
            raise
