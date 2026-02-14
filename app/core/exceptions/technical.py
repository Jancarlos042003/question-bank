from app.core.exceptions.base import TechnicalException


class PersistenceError(TechnicalException):
    """"""

    error_code = "persistence_error"

    def __init__(self, message: str = "Error persisting"):
        super().__init__(message=message, status_code=500)


class StorageError(TechnicalException):
    """"""

    error_code = "storage_error"

    def __init__(self, message: str = "Error storing"):
        super().__init__(message=message, status_code=500)


class StorageBucketNotFoundError(StorageError):
    """"""

    error_code = "storage_bucket_not_found"

    def __init__(self, message: str = "Storage bucket not found"):
        super().__init__(message=message)


class StoragePermissionDeniedError(StorageError):
    """"""

    error_code = "storage_permission_denied"

    def __init__(self, message: str = "Storage permission denied"):
        super().__init__(message=message)
