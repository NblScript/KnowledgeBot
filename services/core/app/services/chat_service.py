"""对话服务"""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, KnowledgeBase, Message, MessageRole


class ChatService:
    """对话服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_conversation(
        self,
        kb_id: str | None = None,
        title: str | None = None,
    ) -> Conversation:
        """创建对话"""
        conv_id = str(uuid.uuid4())
        
        conv = Conversation(
            id=conv_id,
            kb_id=kb_id,
            title=title,
        )
        
        self.session.add(conv)
        await self.session.commit()
        await self.session.refresh(conv)
        
        return conv
    
    async def get_conversation(self, conv_id: str) -> Conversation | None:
        """获取对话"""
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conv_id)
        )
        return result.scalar_one_or_none()
    
    async def list_conversations(
        self,
        kb_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Conversation], int]:
        """获取对话列表"""
        query = select(Conversation)
        count_query = select(func.count(Conversation.id))
        
        if kb_id:
            query = query.where(Conversation.kb_id == kb_id)
            count_query = count_query.where(Conversation.kb_id == kb_id)
        
        query = query.order_by(Conversation.updated_at.desc())
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.session.execute(query)
        convs = list(result.scalars().all())
        
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        return convs, total
    
    async def delete_conversation(self, conv_id: str) -> bool:
        """删除对话"""
        conv = await self.get_conversation(conv_id)
        if not conv:
            return False
        
        await self.session.delete(conv)
        await self.session.commit()
        return True
    
    async def add_message(
        self,
        conv_id: str,
        role: MessageRole,
        content: str,
        token_count: int | None = None,
        sources: list[dict[str, Any]] | None = None,
    ) -> Message:
        """添加消息"""
        msg = Message(
            id=str(uuid.uuid4()),
            conv_id=conv_id,
            role=role,
            content=content,
            token_count=token_count,
            sources=sources,
        )
        
        self.session.add(msg)
        await self.session.commit()
        await self.session.refresh(msg)
        
        return msg
    
    async def get_messages(self, conv_id: str) -> list[Message]:
        """获取对话的所有消息"""
        result = await self.session.execute(
            select(Message)
            .where(Message.conv_id == conv_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())
    
    async def update_conversation_title(
        self, conv_id: str, title: str
    ) -> Conversation | None:
        """更新对话标题"""
        conv = await self.get_conversation(conv_id)
        if conv:
            conv.title = title
            await self.session.commit()
            await self.session.refresh(conv)
        return conv
