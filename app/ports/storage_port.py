from abc import ABC, abstractmethod


class StoragePort(ABC):

    @abstractmethod
    def generate_signed_url(
            self, storage_container_name: str, storage_object_name: str
    ) -> str:
        """
        Genera una URL firmada para lectura
        :param storage_container_name: Nombre del bucket o contenedor donde se encuentra el objeto.
        :param storage_object_name: Nombre o ruta del objeto en el almacenamiento.
        :return: URL firmada con acceso temporal para descarga.
        """
        pass

    @abstractmethod
    def upload_object_from_bytes(
            self,
            storage_container_name: str,
            data: bytes,
            destination: str,
            content_type: str | None = None,
    ) -> str:
        """
        Sube un archivo al bucket.
        :param storage_container_name: Nombre del bucket o contenedor de destino.
        :param data: Contenido binario del archivo a subir.
        :param destination: Ruta o nombre del objeto dentro del contenedor.
        :param content_type: Tipo MIME del contenido (ej. 'image/webp').
        :return: Ruta del archivo en el bucket o contenedor.
        """
        pass
