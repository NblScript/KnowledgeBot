"""文档处理器导出"""

from typing import Any, Callable

from app.processors.docx_processor import DocxProcessor
from app.processors.markdown_processor import MarkdownProcessor
from app.processors.pdf_processor import PDFProcessor
from app.processors.text_processor import chunk_text, estimate_token_count


def get_processor(file_type: str) -> Callable[[str], dict[str, Any]] | None:
    """根据文件类型获取对应的处理器
    
    Args:
        file_type: 文件类型（扩展名）
        
    Returns:
        处理器实例，不支持则返回 None
    """
    file_type = file_type.lower().strip(".")
    
    processors = {
        "pdf": PDFProcessor(),
        "docx": DocxProcessor(),
        "doc": DocxProcessor(),  # 旧版 Word 格式
        "md": MarkdownProcessor(),
        "markdown": MarkdownProcessor(),
    }
    
    return processors.get(file_type)


def get_supported_extensions() -> list[str]:
    """获取支持的文件扩展名"""
    return ["pdf", "docx", "doc", "md", "markdown", "txt"]


def is_supported(file_type: str) -> bool:
    """检查文件类型是否支持"""
    return file_type.lower().strip(".") in get_supported_extensions()


__all__ = [
    "PDFProcessor",
    "DocxProcessor",
    "MarkdownProcessor",
    "chunk_text",
    "estimate_token_count",
    "get_processor",
    "get_supported_extensions",
    "is_supported",
]
