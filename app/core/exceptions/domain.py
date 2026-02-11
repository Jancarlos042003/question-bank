from app.core.exceptions.base import DomainException


class ResourceNotFoundException(DomainException):
    """Raised when a requested domain entity does not exist."""

    error_code = "resource_not_found"

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)
