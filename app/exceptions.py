"""
Custom exceptions for the application.
"""


class DataProcessingError(Exception):
    """Raised when data processing fails."""
    pass


class DataValidationError(Exception):
    """Raised when data validation fails."""
    pass


class AIServiceError(Exception):
    """Raised when AI service encounters an error."""
    pass


class DataSourceError(Exception):
    """Raised when data source cannot be accessed or parsed."""
    pass


