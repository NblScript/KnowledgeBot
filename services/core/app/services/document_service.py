"""文档服务"""

import hashlib
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import milvus_client
from app.models import Chunk, Document, KnowledgeBase
from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentService:
    """文档服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        kb_id: str,
        file_name: str,
        file_path: str | None = None,
        file_size: int | None = None,
        file_type: str | None = None,
        file_hash: str | None = None,
    ) -> Document:
        """创建文档记录"""
        doc_id = str(uuid.uuid4())
        
        doc = Document(
            id=doc_id,
            kb_id=kb_id,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            file_hash=file_hash,
            status="pending",
        )
        
        self.session.add(doc)
        await self.session.commit()
        await self.session.refresh(doc)
        
        return doc
    
    async def get(self, doc_id: str) -> Document | None:
        """获取文档"""
        result = await self.session.execute(
            select(Document).where(Document.id == doc_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_kb(
        self,
        kb_id: str,
        page: int = 1,
        page_size: int = 20,
        status_filter: str | None = None,
    ) -> tuple[list[Document], int]:
        """获取知识库的文档列表"""
        query = select(Document).where(Document.kb_id == kb_id)
        count_query = select(func.count(Document.id)).where(Document.kb_id == kb_id)
        
        if status_filter:
            query = query.where(Document.status == status_filter)
            count_query = count_query.where(Document.status == status_filter)
        
        query = query.order_by(Document.created_at.desc())
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.session.execute(query)
        docs = list(result.scalars().all())
        
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        return docs, total
    
    async def update_status(
        self,
        doc_id: str,
        status: str,
        error_message: str | None = None,
    ) -> Document | None:
        """更新文档状态"""
        doc = await self.get(doc_id)
        if not doc:
            return None
        
        doc.status = status
        if error_message:
            doc.error_message = error_message
        
        await self.session.commit()
        await self.session.refresh(doc)
        return doc
    
    async def update_chunk_count(self, doc_id: str, count: int) -> None:
        """更新文档分块数量"""
        doc = await self.get(doc_id)
        if doc:
            doc.chunk_count = count
            await self.session.commit()
    
    async def delete(self, doc_id: str) -> bool:
        """删除文档"""
        doc = await self.get(doc_id)
        if not doc:
            return False
        
        # 删除 Milvus 中的向量
        milvus_client.delete_by_doc_id(doc.kb_id, doc_id)
        
        await self.session.delete(doc)
        await self.session.commit()
        return True
    
    async def check_duplicate(
        self, kb_id: str, file_hash: str
    ) -> Document | None:
        """检查重复文档"""
        result = await self.session.execute(
            select(Document).where(
                Document.kb_id == kb_id,
                Document.file_hash == file_hash,
            )
        )
        return result.scalar_one_or_none()
    
    async def save_chunks(
        self,
        doc_id: str,
        kb_id: str,
        chunks: list[dict[str, Any]],
        vector_ids: list[int],
    ) -> list[Chunk]:
        """保存文档分块"""
        chunk_records = []
        
        for i, chunk_data in enumerate(chunks):
            chunk = Chunk(
                id=str(uuid.uuid4()),
                doc_id=doc_id,
                kb_id=kb_id,
                content=chunk_data["content"],
                content_hash=hashlib.sha256(
                    chunk_data["content"].encode()
                ).hexdigest(),
                chunk_index=i,
                vector_id=vector_ids[i] if i < len(vector_ids) else None,
                token_count=chunk_data.get("token_count"),
                metadata=chunk_data.get("metadata", {}),
            )
            chunk_records.append(chunk)
            self.session.add(chunk)
        
        await self.session.commit()
        
        # 更新文档分块数量
        await self.update_chunk_count(doc_id, len(chunk_records))
        
        return chunk_records
    
    async def get_chunks(self, doc_id: str) -> list[Chunk]:
        """获取文档的所有分块"""
        result = await self.session.execute(
            select(Chunk)
            .where(Chunk.doc_id == doc_id)
            .order_by(Chunk.chunk_index)
        )
        return list(result.scalars().all())
