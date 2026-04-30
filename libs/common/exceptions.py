"""自定义异常"""


class AppException(Exception):
    """应用异常基类"""
    
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """资源未找到"""
    
    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(message, "NOT_FOUND", details)


class ValidationError(AppException):
    """验证错误"""
    
    def __init__(self, message: str = "Validation error", details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class UnauthorizedError(AppException):
    """未授权"""
    
    def __init__(self, message: str = "Unauthorized", details: dict = None):
        super().__init__(message, "UNAUTHORIZED", details)


class ForbiddenError(AppException):
    """禁止访问"""
    
    def __init__(self, message: str = "Forbidden", details: dict = None):
        super().__init__(message, "FORBIDDEN", details)


class ConflictError(AppException):
    """冲突错误"""
    
    def __init__(self, message: str = "Resource conflict", details: dict = None):
        super().__init__(message, "CONFLICT", details)


class InternalError(AppException):
    """内部错误"""
    
    def __init__(self, message: str = "Internal server error", details: dict = None):
        super().__init__(message, "INTERNAL_ERROR", details)


class ServiceUnavailableError(AppException):
    """服务不可用"""
    
    def __init__(self, service: str = "Service", details: dict = None):
        super().__init__(f"{service} is unavailable", "SERVICE_UNAVAILABLE", details)
