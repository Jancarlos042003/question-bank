from app.ports.storage_port import StoragePort
from fastapi import UploadFile

class ImageService:
    def __init__(self, storage: StoragePort):
        self.storage = storage

    async def upload_image(self, image: UploadFile, storage_container_name: str, destination: str):
        image_bytes = await image.read()

        image_path = self.storage.upload_object_from_bytes(
            storage_container_name=storage_container_name,
            data=image_bytes,
            destination=destination,
            content_type=image.content_type,
        )

        return image_path

    def generate_signature(self, storage_container_name: str, storage_object_name: str):
        url = self.storage.generate_signed_url(
            storage_container_name=storage_container_name,
            storage_object_name=storage_object_name,
        )
        return url
