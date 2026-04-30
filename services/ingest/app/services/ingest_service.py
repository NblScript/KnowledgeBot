"""Ingest Service - 文档摄入服务"""

import hashlib
import time
from typing import Optional

from app.clients.embedding import get_embedding_client
from app.clients.knowledge import get_knowledge_client
from app.config import settings
from app.services.document_processor import ChunkData, DocumentProcessor, get_processor


class IngestService:
    """文档摄入服务"""
    
    def __init__(self):
        self.processor: Optional[DocumentProcessor] = None
    
    def get_processor(self) -> DocumentProcessor:
        """获取文档处理器"""
        if self.processor is None:
            self.processor = get_processor()
        return self.processor
    
    async def process_document(
        self,
        doc_id: str,
        kb_id: str,
        file_content: bytes,
        file_name: str,
        file_type: str,
    ) -> dict:
        """
        处理文档的完整流程
        
        Args:
            doc_id: 文档 ID
            kb_id: 知识库 ID
            file_content: 文件内容（字节）
            file_name: 文件名
            file_type: 文件类型
        
        Returns:
            处理结果
        """
        start_time = time.time()
        
        try:
            # 1. 解析和分块
            processor = self.get_processor()
            parsed, chunks = await processor.process(
                file_content,
                file_name,
                file_type,
            )
            
            if not chunks:
                return {
                    "success": False,
                    "error": "No chunks generated from document",
                    "doc_id": doc_id,
                }
            
            # 2. 向量化
            embedding_client = await get_embedding_client()
            texts = [chunk.content for chunk in chunks]
            vectors = await embedding_client.embed_batch(texts)
            
            # 3. 准备分块数据
            chunk_data_list = []
            for chunk, vector in zip(chunks, vectors):
                chunk_id = hashlib.md5(f"{doc_id}_{chunk.chunk_index}".encode()).hexdigest()[:16]
                chunk_data_list.append({
                    "id": chunk_id,
                    "doc_id": doc_id,
                    "kb_id": kb_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "token_count": chunk.token_count,
                    "vector": vector,
                    "metadata": chunk.metadata,
                })
            
            # 4. 调用 Knowledge Service 存储分块
            knowledge_client = await get_knowledge_client()
            await knowledge_client.create_chunks(doc_id, chunk_data_list)
            
            # 5. 更新文档状态
            processing_time = time.time() - start_time
            total_tokens = sum(c.token_count for c in chunks)
            
            await knowledge_client.update_document_status(
                doc_id,
                status="completed",
                chunk_count=len(chunks),
                metadata={
                    "processing_time": processing_time,
                    "total_tokens": total_tokens,
                    "file_type": file_type,
                },
            )
            
            return {
                "success": True,
                "doc_id": doc_id,
                "chunk_count": len(chunks),
                "total_tokens": total_tokens,
                "processing_time": processing_time,
            }
            
        except Exception as e:
            # 更新文档状态为失败
            try:
                knowledge_client = await get_knowledge_client()
                await knowledge_client.update_document_status(
                    doc_id,
                    status="failed",
                    error_message=str(e),
                )
            except Exception:
                pass
            
            return {
                "success": False,
                "doc_id": doc_id,
                "error": str(e),
            }
    
    async def process_document_from_storage(
        self,
        doc_id: str,
        kb_id: str,
        file_path: str,
        file_name: str,
        file_type: str,
    ) -> dict:
        """
        从 MinIO 存储中读取文件并处理
        
        Args:
            doc_id: 文档 ID
            kb_id: 知识库 ID
            file_path: MinIO 中的文件路径
            file_name: 文件名
            file_type: 文件类型
        
        Returns:
            处理结果
        """
        from minio import Minio
        
        # 从 MinIO 获取文件
        minio_client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        
        response = minio_client.get_object(
            settings.minio_bucket,
            file_path,
        )
        content = response.read()
        response.close()
        response.release_conn()
        
        # 处理文档
        return await self.process_document(
            doc_id=doc_id,
            kb_id=kb_id,
            file_content=content,
            file_name=file_name,
            file_type=file_type,
        )


# 全局实例
_ingest_service: Optional[IngestService] = None


def get_ingest_service() -> IngestService:
    """获取 Ingest Service 实例"""
    global _ingest_service
    if _ingest_service is None:
        _ingest_service = IngestService()
    return _ingest_service