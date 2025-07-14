"""Exception classes for tspy."""


class TspyError(Exception):
    """Base exception for all tspy errors."""
    pass


class TspyAPIError(TspyError):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data