"""Embedding 服务"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.config import settings


class BaseEmbedding(ABC):
    """Embedding 基类"""
    
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """获取文本向量"""
        pass
    
    @abstractmethod
    async def embed_single(self, text: str) -> list[float]:
        """获取单个文本向量"""
        pass


class SiliconFlowEmbedding(BaseEmbedding):
    """SiliconFlow BGE-M3 Embedding"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "BAAI/bge-m3",
        embedding_dim: int = 1024,
    ):
        self.api_key = api_key
        self.model = model
        self.embedding_dim = embedding_dim
        self.base_url = "https://api.siliconflow.cn/v1"
    
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """批量获取向量"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "input": texts,
                    "encoding_format": "float",
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
    
    async def embed_single(self, text: str) -> list[float]:
        """获取单个向量"""
        embeddings = await self.embed([text])
        return embeddings[0]


class OpenAIEmbedding(BaseEmbedding):
    """OpenAI Embedding"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        embedding_dim: int = 1536,
        base_url: str | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self.embedding_dim = embedding_dim
        self.base_url = base_url or "https://api.openai.com/v1"
    
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """批量获取向量"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "input": texts,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
    
    async def embed_single(self, text: str) -> list[float]:
        """获取单个向量"""
        embeddings = await self.embed([text])
        return embeddings[0]


class QwenEmbedding(BaseEmbedding):
    """通义千问 Embedding (DashScope API)"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-v3",
        embedding_dim: int = 1024,
    ):
        self.api_key = api_key
        self.model = model
        self.embedding_dim = embedding_dim
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """批量获取向量"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "input": texts,
                    "dimensions": self.embedding_dim,
                    "encoding_format": "float",
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
    
    async def embed_single(self, text: str) -> list[float]:
        """获取单个向量"""
        embeddings = await self.embed([text])
        return embeddings[0]


# 全局 embedding 实例
_embedding_instance: BaseEmbedding | None = None


def get_embedder() -> BaseEmbedding:
    """获取 Embedding 实例"""
    global _embedding_instance
    
    if _embedding_instance is None:
        if settings.embedding_provider == "siliconflow":
            _embedding_instance = SiliconFlowEmbedding(
                api_key=settings.siliconflow_api_key,
                model=settings.embedding_model,
                embedding_dim=settings.embedding_dim,
            )
        elif settings.embedding_provider == "openai":
            _embedding_instance = OpenAIEmbedding(
                api_key=settings.openai_api_key,
                model=settings.embedding_model,
                embedding_dim=settings.embedding_dim,
                base_url=settings.openai_base_url,
            )
        elif settings.embedding_provider == "qwen":
            _embedding_instance = QwenEmbedding(
                api_key=settings.qwen_api_key,
                model=settings.embedding_model,
                embedding_dim=settings.embedding_dim,
            )
        else:
            raise ValueError(f"Unknown embedding provider: {settings.embedding_provider}")
    
    return _embedding_instance
