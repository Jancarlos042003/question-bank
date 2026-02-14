from app.core.exceptions.base import TechnicalException


class PersistenceError(TechnicalException):
    """Error al persistir datos en la base de datos."""

    error_code = "persistence_error"

    def __init__(self, message: str = "Error persisting"):
        super().__init__(message=message, status_code=500)


class StorageError(TechnicalException):
    """Errores relacionados con el almacenamiento de archivos."""

    error_code = "storage_error"

    def __init__(self, message: str = "Error storing"):
        super().__init__(message=message, status_code=500)


class StorageBucketNotFoundError(StorageError):
    """El bucket de almacenamiento no existe."""

    error_code = "storage_bucket_not_found"

    def __init__(self, message: str = "Storage bucket not found"):
        super().__init__(message=message)


class StoragePermissionDeniedError(StorageError):
    """No se tienen permisos para acceder al almacenamiento."""

    error_code = "storage_permission_denied"

    def __init__(self, message: str = "Storage permission denied"):
        super().__init__(message=message)
