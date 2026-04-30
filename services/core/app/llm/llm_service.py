"""LLM 服务"""

import abc
import json
from typing import Any

import httpx

from app.config import settings


class BaseLLM(abc.ABC):
    """LLM 基类"""
    
    @abc.abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """生成回答"""
        pass
    
    @abc.abstractmethod
    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """流式生成"""
        pass


class ZhipuLLM(BaseLLM):
    """智谱 GLM LLM"""
    
    def __init__(self, api_key: str, model: str = "glm-4"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
    
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """生成回答"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """流式生成"""
        async with httpx.AsyncClient() as client:
            response = await client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
                timeout=60.0,
            )
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and data["choices"]:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue


class OpenAILLM(BaseLLM):
    """OpenAI LLM"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.openai.com/v1"
    
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """生成回答"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """流式生成"""
        async with httpx.AsyncClient() as client:
            response = await client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
                timeout=60.0,
            )
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and data["choices"]:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue


# RAG Prompt
SYSTEM_PROMPT = """你是一个专业的知识库助手。基于提供的参考资料回答用户问题。

回答要求：
1. 仅使用参考资料中的信息回答
2. 如果参考资料没有相关信息，明确告知用户
3. 回答要准确、简洁、专业
4. 引用具体的来源"""


def build_rag_prompt(query: str, contexts: list[dict[str, Any]]) -> str:
    """构建 RAG 提示词"""
    context_text = "\n\n---\n\n".join([
        f"【来源 {i+1}】{ctx['doc_name']} (页码: {ctx.get('page', 'N/A')})\n{ctx['content']}"
        for i, ctx in enumerate(contexts)
    ])
    
    return f"""参考资料：
{context_text}

用户问题：{query}

请基于参考资料回答用户问题："""


# 全局 LLM 实例
_llm_instance: BaseLLM | None = None


def get_llm() -> BaseLLM:
    """获取 LLM 实例"""
    global _llm_instance
    
    if _llm_instance is None:
        if settings.llm_provider == "zhipu":
            _llm_instance = ZhipuLLM(
                api_key=settings.zhipu_api_key,
                model=settings.llm_model,
            )
        elif settings.llm_provider == "openai":
            _llm_instance = OpenAILLM(
                api_key=settings.openai_api_key,
                model=settings.llm_model,
                base_url=settings.openai_base_url,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
    
    return _llm_instance