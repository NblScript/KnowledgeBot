"""Celery 任务 - 异步文档处理"""

from app.celery_app import celery_app
from app.config import settings
from app.database import async_session_factory
from app.models import Chunk, Document
from app.services.document_processor import get_processor
from app.database import milvus_client
from sqlalchemy import select


@celery_app.task(bind=True)
def process_document_task(self, doc_id: str):
    """异步处理文档任务"""
    import asyncio
    
    # 创建事件循环运行异步代码
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(_process_document_async(doc_id))
    finally:
        loop.close()


async def _process_document_async(doc_id: str):
    """异步处理文档"""
    from minio import Minio
    
    async with async_session_factory() as session:
        # 获取文档记录
        result = await session.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            print(f"Document {doc_id} not found")
            return
        
        try:
            # 更新状态为处理中
            doc.status = "processing"
            await session.commit()
            
            # 从 MinIO 获取文件内容
            minio_client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure,
            )
            
            response = minio_client.get_object(
                settings.minio_bucket,
                doc.file_path,
            )
            content = response.read()
            response.close()
            response.release_conn()
            
            # 处理文档
            processor = get_processor()
            parsed, chunks = await processor.process(
                content,
                doc.file_name,
                doc.file_type,
            )
            
            # 向量化分块
            vectors = await processor.embed_chunks(
                chunks,
                doc.kb_id,
                doc.id,
            )
            
            # 存储到 Milvus
            if vectors:
                milvus_client.insert(
                    collection_name=doc.kb_id,
                    data=vectors,
                )
            
            # 存储到数据库
            for chunk in chunks:
                chunk_record = Chunk(
                    id=hashlib.md5(f"{doc_id}_{chunk.chunk_index}".encode()).hexdigest()[:16],
                    doc_id=doc.id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    token_count=chunk.token_count,
                    metadata_=chunk.metadata,
                )
                session.add(chunk_record)
            
            # 更新文档状态
            doc.status = "completed"
            doc.chunk_count = len(chunks)
            await session.commit()
            
            print(f"Document {doc_id} processed successfully: {len(chunks)} chunks")
            
        except Exception as e:
            # 更新状态为失败
            doc.status = "failed"
            doc.error_message = str(e)
            await session.commit()
            print(f"Failed to process document {doc_id}: {e}")
            raise


import hashlib


@celery_app.task
def health_check():
    """健康检查任务"""
    return {"status": "ok", "provider": settings.llm_provider}
