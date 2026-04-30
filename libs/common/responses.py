"""统一响应格式"""

from typing import Any, Optional, List
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = True
    data: Any
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: dict
    message: str


class PaginateMeta(BaseModel):
    """分页元数据"""
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginateResponse(BaseModel):
    """分页响应"""
    success: bool = True
    data: List[Any]
    meta: PaginateMeta


def success_response(
    data: Any,
    message: Optional[str] = None,
) -> dict:
    """成功响应"""
    return {
        "success": True,
        "data": data,
        "message": message,
    }


def error_response(
    code: str,
    message: str,
    details: Optional[dict] = None,
) -> dict:
    """错误响应"""
    return {
        "success": False,
        "error": {
            "code": code,
            "details": details or {},
        },
        "message": message,
    }


def paginate_response(
    data: List[Any],
    total: int,
    page: int,
    page_size: int,
) -> dict:
    """分页响应"""
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {
        "success": True,
        "data": data,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }