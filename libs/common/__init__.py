"""共享库 - 通用工具"""

from .config import BaseSettings, get_settings
from .exceptions import (
    AppException,
    NotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    InternalError,
)
from .logging import setup_logging, get_logger
from .responses import success_response, error_response, paginate_response

__all__ = [
    # Config
    "BaseSettings",
    "get_settings",
    # Exceptions
    "AppException",
    "NotFoundError",
    "ValidationError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "InternalError",
    # Logging
    "setup_logging",
    "get_logger",
    # Responses
    "success_response",
    "error_response",
    "paginate_response",
]
