"""对话路由"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.models import Conversation, KnowledgeBase, Message
from app.schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatChoice,
    ChatUsage,
    ConversationListResponse,
    ConversationResponse,
    ConversationCreate,
    MessageCreate,
    MessageResponse,
    SourceReference,
)
from app.schemas.common import PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post("/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    session: AsyncSession = Depends(get_session),
):
    """创建对话补全（非流式）"""
    # 检查知识库
    kb_result = await session.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == request.kb_id)
    )
    kb = kb_result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {request.kb_id} not found",
        )
    
    # 获取或创建对话
    conversation = None
    if request.conversation_id:
        conv_result = await session.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found",
            )
    else:
        # 创建新对话
        conv_id = str(uuid.uuid4())
        conversation = Conversation(
            id=conv_id,
            kb_id=request.kb_id,
            title=request.messages[0].content[:50] if request.messages else "New Chat",
        )
        session.add(conversation)
        await session.flush()
    
    # 获取用户消息
    user_message_content = request.messages[-1].content if request.messages else ""
    
    # TODO: 调用 Embedding 服务获取向量
    # TODO: 调用 Milvus 检索相关内容
    # TODO: 调用 LLM 生成回答
    
    # 模拟响应（实际需要调用 LLM 服务）
    response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    
    # 保存用户消息
    user_msg = Message(
        id=str(uuid.uuid4()),
        conv_id=conversation.id,
        role="user",
        content=user_message_content,
    )
    session.add(user_msg)
    
    # 保存助手消息
    assistant_msg = Message(
        id=str(uuid.uuid4()),
        conv_id=conversation.id,
        role="assistant",
        content="这是一个模拟的回答。实际实现需要连接 LLM 服务。",
        sources=[],
    )
    session.add(assistant_msg)
    
    await session.commit()
    
    return ChatCompletionResponse(
        id=response_id,
        conversation_id=conversation.id,
        kb_id=request.kb_id,
        choices=[
            ChatChoice(
                index=0,
                message=MessageCreate(
                    role="assistant",
                    content="这是一个模拟的回答。实际实现需要连接 LLM 服务。",
                ),
                finish_reason="stop",
            )
        ],
        sources=[],
        usage=ChatUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        ),
        created_at=assistant_msg.created_at,
    )


@router.get("/conversations", response_model=PaginatedResponse[ConversationListResponse])
async def list_conversations(
    kb_id: str | None = Query(None, description="知识库 ID 过滤"),
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    session: AsyncSession = Depends(get_session),
):
    """获取对话列表"""
    # 构建查询
    query = select(Conversation)
    count_query = select(func.count(Conversation.id))
    
    if kb_id:
        query = query.where(Conversation.kb_id == kb_id)
        count_query = count_query.where(Conversation.kb_id == kb_id)
    
    # 排序和分页
    query = query.order_by(Conversation.updated_at.desc())
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # 执行查询
    result = await session.execute(query)
    convs = result.scalars().all()
    
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    items = []
    for conv in convs:
        # 统计消息数量
        msg_count_result = await session.execute(
            select(func.count(Message.id)).where(Message.conv_id == conv.id)
        )
        msg_count = msg_count_result.scalar() or 0
        
        items.append(ConversationListResponse(
            id=conv.id,
            kb_id=conv.kb_id,
            title=conv.title,
            message_count=msg_count,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        ))
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/conversations/{conv_id}", response_model=ConversationResponse)
async def get_conversation(
    conv_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取对话详情"""
    result = await session.execute(
        select(Conversation).where(Conversation.id == conv_id)
    )
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conv_id} not found",
        )
    
    # 获取消息列表
    msg_result = await session.execute(
        select(Message)
        .where(Message.conv_id == conv_id)
        .order_by(Message.created_at)
    )
    messages = msg_result.scalars().all()
    
    return ConversationResponse(
        id=conv.id,
        kb_id=conv.kb_id,
        title=conv.title,
        message_count=len(messages),
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role.value if hasattr(msg.role, "value") else msg.role,
                content=msg.content,
                token_count=msg.token_count,
                sources=msg.sources,
                created_at=msg.created_at,
            )
            for msg in messages
        ],
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.delete("/conversations/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conv_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除对话"""
    result = await session.execute(
        select(Conversation).where(Conversation.id == conv_id)
    )
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conv_id} not found",
        )
    
    await session.delete(conv)
    await session.commit()
    
    return None
