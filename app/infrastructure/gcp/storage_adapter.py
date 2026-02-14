import datetime

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

    # https://docs.cloud.google.com/storage/docs/access-control/signing-urls-with-helpers?hl=es-419#download-object
    def generate_signed_url(
            self, storage_container_name: str, storage_object_name: str
    ) -> str:
        bucket = self.storage_client.bucket(storage_container_name)
        blob = bucket.blob(storage_object_name)

        # Se puede ver la existencia del blob con blob.exists()

        # La URL firmada solo valida permisos y expiración, no existencia del blob.
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15),
            method="GET",
        )

        return url

    # https://docs.cloud.google.com/storage/docs/uploading-objects-from-memory?hl=es-419#uploading-an-object-from-memory
    def upload_object_from_bytes(
            self,
            storage_container_name: str,
            data: bytes,
            destination: str,
            content_type: str | None = None,
    ):
        bucket = self.storage_client.bucket(storage_container_name)
        blob = bucket.blob(destination)

        blob.upload_from_string(data, content_type=content_type)

        return destination[1:]
