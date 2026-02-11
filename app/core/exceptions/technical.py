from app.core.exceptions.base import TechnicalException


class PersistenceError(TechnicalException):
    """Raised when question persistence fails."""

    error_code = "persistence_error"

    def __init__(self, message: str = "Error persisting"):
        super().__init__(message=message, status_code=500)
