"""日志配置"""

import logging
import sys
from typing import Optional

from .config import get_settings


def setup_logging(
    level: Optional[str] = None,
    format_type: Optional[str] = None,
) -> None:
    """设置日志"""
    settings = get_settings()
    
    log_level = level or settings.log_level
    log_format = format_type or settings.log_format
    
    # 日志格式
    if log_format == "json":
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", '
            '"name": "%(name)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
    
    # 配置根日志
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有 handlers
    root_logger.handlers.clear()
    
    # 添加控制台 handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """获取 logger"""
    return logging.getLogger(name)
