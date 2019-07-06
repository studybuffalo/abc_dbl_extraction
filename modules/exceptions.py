"""Custom exceptions to handle application errors."""

class ImproperlyConfigured(Exception):
    """Exception raised due to improperly configured settings."""

class ExtractionError(Exception):
    """Exception raised due to issue with HTML extraction."""
