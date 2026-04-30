"""消息模型"""

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MessageRole(str, enum.Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base):
    """消息表"""
    
    __tablename__ = "messages"
    __table_args__ = {"schema": "chat"}  # 使用 chat schema
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conv_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chat.conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[MessageRole] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sources: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )
    
    # 关联关系
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
    )


# 导入 Conversation 以解决循环引用
from app.models.conversation import Conversation  # noqa
