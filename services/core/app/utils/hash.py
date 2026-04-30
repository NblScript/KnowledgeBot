"""哈希工具"""

import hashlib


def compute_hash(content: str) -> str:
    """计算内容哈希"""
    return hashlib.sha256(content.encode()).hexdigest()


def compute_file_hash(content: bytes) -> str:
    """计算文件哈希"""
    return hashlib.sha256(content).hexdigest()