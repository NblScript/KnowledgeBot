"""对话模型"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.message import Message


class Conversation(Base, TimestampMixin):
    """对话表"""
    
    __tablename__ = "conversations"
    __table_args__ = {"schema": "chat"}  # 使用 chat schema
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    kb_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
        comment="知识库 ID（来自 Core Service）",
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # 关联关系
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    
    @property
    def message_count(self) -> int:
        """消息数量"""
        return len(self.messages) if self.messages else 0
