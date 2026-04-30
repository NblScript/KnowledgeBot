"""Embedding 服务 - 支持 OpenAI/Qwen/SiliconFlow"""

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
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """返回模型名称"""
        pass
    
    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """返回向量维度"""
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
        self._model = model
        self._embedding_dim = embedding_dim
        self.base_url = "https://api.siliconflow.cn/v1"
    
    @property
    def model_name(self) -> str:
        return self._model
    
    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim
    
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
                    "model": self._model,
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
        self._model = model
        self._embedding_dim = embedding_dim
        self.base_url = base_url or "https://api.openai.com/v1"
    
    @property
    def model_name(self) -> str:
        return self._model
    
    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim
    
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
                    "model": self._model,
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
        self._model = model
        self._embedding_dim = embedding_dim
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    @property
    def model_name(self) -> str:
        return self._model
    
    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim
    
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
                    "model": self._model,
                    "input": texts,
                    "dimensions": self._embedding_dim,
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


class MockEmbedding(BaseEmbedding):
    """Mock Embedding (用于测试)"""
    
    def __init__(self, embedding_dim: int = 1536):
        self._embedding_dim = embedding_dim
        self._model = "mock-embedding"
    
    @property
    def model_name(self) -> str:
        return self._model
    
    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim
    
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """返回随机向量"""
        import random
        return [[random.random() for _ in range(self._embedding_dim)] for _ in texts]
    
    async def embed_single(self, text: str) -> list[float]:
        embeddings = await self.embed([text])
        return embeddings[0]


class EmbeddingService:
    """Embedding 服务封装"""
    
    def __init__(self, provider: str | None = None):
        self._embedder: BaseEmbedding | None = None
        self._provider = provider or settings.embedding_provider
    
    def _create_embedder(self) -> BaseEmbedding:
        """创建 Embedder 实例"""
        if self._provider == "siliconflow":
            return SiliconFlowEmbedding(
                api_key=settings.siliconflow_api_key,
                model=settings.embedding_model,
                embedding_dim=settings.embedding_dim,
            )
        elif self._provider == "openai":
            return OpenAIEmbedding(
                api_key=settings.openai_api_key,
                model=settings.embedding_model,
                embedding_dim=settings.embedding_dim,
                base_url=settings.openai_base_url,
            )
        elif self._provider == "qwen":
            return QwenEmbedding(
                api_key=settings.qwen_api_key,
                model=settings.embedding_model,
                embedding_dim=settings.embedding_dim,
            )
        elif self._provider == "mock":
            return MockEmbedding(embedding_dim=settings.embedding_dim)
        else:
            raise ValueError(f"Unknown embedding provider: {self._provider}")
    
    @property
    def embedder(self) -> BaseEmbedding:
        """获取 Embedder 实例"""
        if self._embedder is None:
            self._embedder = self._create_embedder()
        return self._embedder
    
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量获取向量"""
        # 分批处理
        batch_size = settings.embedding_batch_size
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = await self.embedder.embed(batch)
            all_embeddings.extend(embeddings)
        
        return all_embeddings
    
    async def embed_single(self, text: str) -> list[float]:
        """获取单个向量"""
        return await self.embedder.embed_single(text)
    
    @property
    def model_name(self) -> str:
        return self.embedder.model_name
    
    @property
    def embedding_dim(self) -> int:
        return self.embedder.embedding_dim


# 全局服务实例
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """获取 Embedding 服务实例"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service