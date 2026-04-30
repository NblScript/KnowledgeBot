"""知识库模型"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.conversation import Conversation


class KnowledgeBase(Base, TimestampMixin):
    """知识库表"""
    
    __tablename__ = "knowledge_bases"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_model: Mapped[str] = mapped_column(String(100), default="bge-m3")
    llm_model: Mapped[str] = mapped_column(String(100), default="glm-4")
    embedding_dim: Mapped[int] = mapped_column(Integer, default=1024)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, archived
    
    # 关联关系
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )
    
    @property
    def document_count(self) -> int:
        """文档数量"""
        return len(self.documents) if self.documents else 0
    
    @property
    def chunk_count(self) -> int:
        """分块总数"""
        if not self.documents:
            return 0
        return sum(doc.chunk_count or 0 for doc in self.documents)
