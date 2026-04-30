"""LLM 模块导出"""

from app.llm.llm_service import (
    BaseLLM,
    ZhipuLLM,
    OpenAILLM,
    get_llm,
    build_rag_prompt,
    SYSTEM_PROMPT,
)

__all__ = [
    "BaseLLM",
    "ZhipuLLM",
    "OpenAILLM",
    "get_llm",
    "build_rag_prompt",
    "SYSTEM_PROMPT",
]