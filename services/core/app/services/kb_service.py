"""知识库服务"""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import milvus_client
from app.models import Chunk, Document, KnowledgeBase
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate


class KnowledgeBaseService:
    """知识库服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: KnowledgeBaseCreate) -> KnowledgeBase:
        """创建知识库"""
        kb_id = str(uuid.uuid4())
        
        kb = KnowledgeBase(
            id=kb_id,
            name=data.name,
            description=data.description,
            embedding_model=data.embedding_model,
            llm_model=data.llm_model,
            status="active",
        )
        
        self.session.add(kb)
        await self.session.commit()
        await self.session.refresh(kb)
        
        # 创建 Milvus Collection
        milvus_client.create_collection(kb_id, embedding_dim=1024)
        
        return kb
    
    async def get(self, kb_id: str) -> KnowledgeBase | None:
        """获取知识库"""
        result = await self.session.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: str | None = None,
    ) -> tuple[list[KnowledgeBase], int]:
        """获取知识库列表"""
        query = select(KnowledgeBase)
        count_query = select(func.count(KnowledgeBase.id))
        
        if status_filter:
            query = query.where(KnowledgeBase.status == status_filter)
            count_query = count_query.where(KnowledgeBase.status == status_filter)
        
        query = query.order_by(KnowledgeBase.created_at.desc())
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.session.execute(query)
        kbs = list(result.scalars().all())
        
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        return kbs, total
    
    async def update(
        self, kb_id: str, data: KnowledgeBaseUpdate
    ) -> KnowledgeBase | None:
        """更新知识库"""
        kb = await self.get(kb_id)
        if not kb:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(kb, key, value)
        
        await self.session.commit()
        await self.session.refresh(kb)
        return kb
    
    async def delete(self, kb_id: str) -> bool:
        """删除知识库"""
        kb = await self.get(kb_id)
        if not kb:
            return False
        
        # 删除 Milvus Collection
        milvus_client.drop_collection(kb_id)
        
        await self.session.delete(kb)
        await self.session.commit()
        return True
    
    async def get_stats(self, kb_id: str) -> dict[str, Any]:
        """获取知识库统计信息"""
        doc_count_result = await self.session.execute(
            select(func.count(Document.id)).where(Document.kb_id == kb_id)
        )
        doc_count = doc_count_result.scalar() or 0
        
        chunk_count_result = await self.session.execute(
            select(func.count(Chunk.id)).where(Chunk.kb_id == kb_id)
        )
        chunk_count = chunk_count_result.scalar() or 0
        
        # 按状态统计文档
        status_counts = {}
        status_result = await self.session.execute(
            select(Document.status, func.count(Document.id))
            .where(Document.kb_id == kb_id)
            .group_by(Document.status)
        )
        for status, count in status_result:
            status_counts[status] = count
        
        return {
            "document_count": doc_count,
            "chunk_count": chunk_count,
            "document_status": status_counts,
        }
