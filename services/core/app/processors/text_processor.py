"""文档处理任务"""

import hashlib
from typing import Any

from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings


CHUNK_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "separators": ["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " ", ""],
}


def chunk_text(text: str, metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """文本分块
    
    Args:
        text: 原始文本
        metadata: 元数据（页码、标题等）
        
    Returns:
        分块列表
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_CONFIG["chunk_size"],
        chunk_overlap=CHUNK_CONFIG["chunk_overlap"],
        separators=CHUNK_CONFIG["separators"],
        length_function=len,
    )
    
    chunks = splitter.split_text(text)
    
    return [
        {
            "content": chunk,
            "chunk_index": i,
            "metadata": metadata or {},
        }
        for i, chunk in enumerate(chunks)
    ]


def estimate_token_count(text: str) -> int:
    """估算 token 数量（简单估计：4字符≈1token）"""
    return len(text) // 4