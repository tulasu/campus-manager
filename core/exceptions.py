"""Custom exceptions for Campus Manager application."""


class CampusManagerException(Exception):
    """Base exception for Campus Manager application."""
    pass


class DataValidationError(CampusManagerException):
    """Raised when data validation fails."""
    pass


class SheetNotFoundError(CampusManagerException):
    """Raised when a Google Sheet is not found or inaccessible."""
    pass


class ConfigurationError(CampusManagerException):
    """Raised when application configuration is invalid."""
    pass


class CalculationError(CampusManagerException):
    """Raised when distribution calculation fails."""
    pass