class AppException(Exception):
    """Excepción base para errores de la aplicación."""

    status_code = 500
    error_code = "app_error"

    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class DomainException(AppException):
    """Excepción de reglas de negocio/dominio."""

    status_code = 400
    error_code = "domain_error"


class TechnicalException(AppException):
    """Excepción de infraestructura/persistencia."""

    status_code = 500
    error_code = "technical_error"
