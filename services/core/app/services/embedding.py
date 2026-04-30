"""Embedding 服务 - 支持多种向量模型提供商"""

import asyncio
from abc import ABC, abstractmethod
from typing import List

import httpx
from pydantic import BaseModel

from app.config import settings


class EmbeddingResult(BaseModel):
    """Embedding 结果"""
    vectors: List[List[float]]
    model: str
    dimension: int
    tokens_used: int = 0


class EmbeddingProvider(ABC):
    """Embedding 提供商基类"""
    
    @abstractmethod
    async def embed(self, texts: List[str]) -> EmbeddingResult:
        """生成文本向量"""
        pass
    
    @abstractmethod
    async def embed_single(self, text: str) -> List[float]:
        """生成单个文本向量"""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """向量维度"""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """模型名称"""
        pass


class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI Embedding 服务"""
    
    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self._model = model
        self._api_key = api_key or settings.openai_api_key
        self._base_url = base_url or settings.openai_base_url or "https://api.openai.com/v1"
        
        # 根据模型确定维度
        self._dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
    
    @property
    def dimension(self) -> int:
        return self._dimensions.get(self._model, 1536)
    
    @property
    def model_name(self) -> str:
        return self._model
    
    async def embed(self, texts: List[str]) -> EmbeddingResult:
        """调用 OpenAI API 生成向量"""
        if not self._api_key:
            raise ValueError("OpenAI API key not configured")
        
        url = f"{self._base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json={
                    "model": self._model,
                    "input": texts,
                    "encoding_format": "float",
                },
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            vectors = [item["embedding"] for item in data["data"]]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            
            return EmbeddingResult(
                vectors=vectors,
                model=self._model,
                dimension=self.dimension,
                tokens_used=tokens_used,
            )
    
    async def embed_single(self, text: str) -> List[float]:
        """生成单个文本向量"""
        result = await self.embed([text])
        return result.vectors[0]


class LocalEmbedding(EmbeddingProvider):
    """本地 Embedding 服务 (使用 sentence-transformers)"""
    
    def __init__(
        self,
        model: str = "BAAI/bge-m3",
        device: str = "cpu",
    ):
        self._model_name = model
        self._device = device
        self._model_instance = None
        
        # 常用模型的维度映射
        self._dimensions = {
            "BAAI/bge-m3": 1024,
            "BAAI/bge-large-zh": 1024,
            "BAAI/bge-small-zh": 512,
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "sentence-transformers/all-mpnet-base-v2": 768,
        }
    
    def _load_model(self):
        """延迟加载模型"""
        if self._model_instance is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model_instance = SentenceTransformer(self._model_name, device=self._device)
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
        return self._model_instance
    
    @property
    def dimension(self) -> int:
        return self._dimensions.get(self._model_name, 768)
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    async def embed(self, texts: List[str]) -> EmbeddingResult:
        """使用本地模型生成向量"""
        model = self._load_model()
        
        # 在线程池中运行，避免阻塞
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: model.encode(texts, normalize_embeddings=True).tolist()
        )
        
        return EmbeddingResult(
            vectors=embeddings,
            model=self._model_name,
            dimension=self.dimension,
            tokens_used=0,  # 本地模型不计算 token
        )
    
    async def embed_single(self, text: str) -> List[float]:
        """生成单个文本向量"""
        result = await self.embed([text])
        return result.vectors[0]


class MockEmbedding(EmbeddingProvider):
    """模拟 Embedding 服务 (用于测试)"""
    
    def __init__(self, dimension: int = 1024):
        self._dimension = dimension
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    @property
    def model_name(self) -> str:
        return "mock-embedding"
    
    async def embed(self, texts: List[str]) -> EmbeddingResult:
        """生成随机向量"""
        import random
        vectors = [[random.random() for _ in range(self._dimension)] for _ in texts]
        return EmbeddingResult(
            vectors=vectors,
            model="mock-embedding",
            dimension=self._dimension,
            tokens_used=0,
        )
    
    async def embed_single(self, text: str) -> List[float]:
        result = await self.embed([text])
        return result.vectors[0]


class QwenEmbedding(EmbeddingProvider):
    """通义千问 Embedding 服务"""
    
    def __init__(
        self,
        model: str = "text-embedding-v3",
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self._model = model
        self._api_key = api_key or settings.qwen_api_key
        self._base_url = base_url or settings.qwen_base_url
        
        # 通义千问 embedding 维度
        self._dimensions = {
            "text-embedding-v1": 1536,
            "text-embedding-v2": 1536,
            "text-embedding-v3": 1024,
        }
    
    @property
    def dimension(self) -> int:
        return self._dimensions.get(self._model, 1024)
    
    @property
    def model_name(self) -> str:
        return self._model
    
    async def embed(self, texts: List[str]) -> EmbeddingResult:
        """调用通义千问 API"""
        if not self._api_key:
            raise ValueError("Qwen API key not configured")
        
        url = f"{self._base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json={
                    "model": self._model,
                    "input": texts,
                    "dimensions": self.dimension,
                },
            )
            
            if response.status_code != 200:
                raise Exception(f"Qwen API error: {response.status_code} - {response.text}")
            
            data = response.json()
            vectors = [item["embedding"] for item in data["data"]]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            
            return EmbeddingResult(
                vectors=vectors,
                model=self._model,
                dimension=self.dimension,
                tokens_used=tokens_used,
            )
    
    async def embed_single(self, text: str) -> List[float]:
        result = await self.embed([text])
        return result.vectors[0]


class SiliconFlowEmbedding(EmbeddingProvider):
    """SiliconFlow Embedding 服务"""
    
    def __init__(
        self,
        model: str = "BAAI/bge-m3",
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self._model = model
        self._api_key = api_key or settings.siliconflow_api_key
        self._base_url = base_url or settings.siliconflow_base_url
        
        self._dimensions = {
            "BAAI/bge-m3": 1024,
            "BAAI/bge-large-zh-v1.5": 1024,
            "jinaai/jina-embeddings-v2-base-zh": 768,
        }
    
    @property
    def dimension(self) -> int:
        return self._dimensions.get(self._model, 1024)
    
    @property
    def model_name(self) -> str:
        return self._model
    
    async def embed(self, texts: List[str]) -> EmbeddingResult:
        if not self._api_key:
            raise ValueError("SiliconFlow API key not configured")
        
        url = f"{self._base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json={
                    "model": self._model,
                    "input": texts,
                    "encoding_format": "float",
                },
            )
            
            if response.status_code != 200:
                raise Exception(f"SiliconFlow API error: {response.status_code} - {response.text}")
            
            data = response.json()
            vectors = [item["embedding"] for item in data["data"]]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            
            return EmbeddingResult(
                vectors=vectors,
                model=self._model,
                dimension=self.dimension,
                tokens_used=tokens_used,
            )
    
    async def embed_single(self, text: str) -> List[float]:
        result = await self.embed([text])
        return result.vectors[0]


def get_embedding_service() -> EmbeddingProvider:
    """获取 Embedding 服务实例"""
    provider = settings.embedding_provider.lower()
    
    if provider == "openai":
        return OpenAIEmbedding(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    elif provider == "local":
        return LocalEmbedding(
            model=settings.embedding_model,
            device=settings.embedding_device,
        )
    elif provider == "qwen":
        return QwenEmbedding(
            model=settings.embedding_model,
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
        )
    elif provider == "siliconflow":
        return SiliconFlowEmbedding(
            model=settings.embedding_model,
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_base_url,
        )
    elif provider == "mock":
        return MockEmbedding(dimension=settings.embedding_dim)
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")


# 全局实例 (延迟初始化)
_embedding_service: EmbeddingProvider | None = None


def get_embedding() -> EmbeddingProvider:
    """获取全局 Embedding 服务"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = get_embedding_service()
    return _embedding_service
