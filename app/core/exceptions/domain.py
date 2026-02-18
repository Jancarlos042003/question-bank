from app.core.exceptions.base import DomainException


class ResourceNotFoundException(DomainException):
    """No se encuentra un recurso"""

    error_code = "resource_not_found"

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class DuplicateValueError(DomainException):
    """Valor duplicado"""

    error_code = "duplicate_value"

    def __init__(self, message: str = "Duplicate value"):
        super().__init__(message=message, status_code=409)


class ForeignKeyViolationError(DomainException):
    """Violación de clave foránea"""

    error_code = "foreign_key_violation"

    def __init__(self, message: str = "Foreign key violation"):
        super().__init__(message=message, status_code=400)


# QUESTION
class MultipleCorrectChoicesError(DomainException):
    """Más de una alternativa marcada como correcta"""

    error_code = "multiple_correct_choices"

    def __init__(self, message: str = "Multiple correct choices"):
        super().__init__(message=message, status_code=400)


class NoCorrectChoiceError(DomainException):
    """No se encontró ninguna alternativa correcta"""

    error_code = "no_correct_choice"

    def __init__(self, message: str = "No correct choice"):
        super().__init__(message=message, status_code=400)


class DuplicateChoiceContentError(DomainException):
    """Contenido duplicado en las alternativas"""

    error_code = "duplicate_choice_content"

    def __init__(self, message: str = "Duplicate choice content"):
        super().__init__(message=message, status_code=400)


# IMAGE
class ContentTypeError(DomainException):
    """Tipo de contenido no válido"""

    error_code = "content_type_error"

    def __init__(self, message: str = "Content type error"):
        super().__init__(message=message, status_code=400)
