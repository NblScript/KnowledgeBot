"""对话路由"""

import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.llm.llm_service import SYSTEM_PROMPT, build_rag_prompt, get_llm
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
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post("/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    session: AsyncSession = Depends(get_session),
):
    """创建对话补全（非流式）- RAG 问答"""
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
    
    # ========== RAG 核心逻辑 ==========
    
    # 1. 检索相关内容
    retrieval_service = RetrievalService(session)
    search_results = await retrieval_service.search(
        kb_id=request.kb_id,
        query=user_message_content,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
    )
    
    # 2. 构建 RAG 提示词
    contexts = [
        {
            "content": r["content"],
            "doc_name": r.get("doc_name", "Unknown"),
            "doc_id": r["doc_id"],
            "chunk_id": r["chunk_id"],
            "score": r["score"],
            "page": r.get("metadata", {}).get("page", "N/A"),
        }
        for r in search_results
    ]
    
    rag_prompt = build_rag_prompt(user_message_content, contexts)
    
    # 3. 构建消息列表
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    
    # 添加历史消息（如果有）
    if request.conversation_id:
        msg_result = await session.execute(
            select(Message)
            .where(Message.conv_id == request.conversation_id)
            .order_by(Message.created_at)
        )
        history_messages = msg_result.scalars().all()
        
        # 只保留最近 N 条历史消息（避免上下文过长）
        max_history = 10
        history_messages = history_messages[-max_history:] if len(history_messages) > max_history else history_messages
        
        for msg in history_messages:
            messages.append({
                "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                "content": msg.content,
            })
    
    # 添加当前 RAG 提示
    messages.append({"role": "user", "content": rag_prompt})
    
    # 4. 调用 LLM 生成回答
    llm = get_llm()
    assistant_response = await llm.generate(
        messages=messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    
    # 5. 构建响应
    response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    
    # 保存用户消息
    user_msg = Message(
        id=str(uuid.uuid4()),
        conv_id=conversation.id,
        role="user",
        content=user_message_content,
    )
    session.add(user_msg)
    
    # 构建来源引用
    sources = [
        SourceReference(
            chunk_id=ctx["chunk_id"],
            doc_id=ctx["doc_id"],
            doc_name=ctx["doc_name"],
            content=ctx["content"][:500],  # 截断显示
            score=ctx["score"],
            metadata={"page": ctx.get("page")},
        )
        for ctx in contexts
    ]
    
    # 保存助手消息
    assistant_msg = Message(
        id=str(uuid.uuid4()),
        conv_id=conversation.id,
        role="assistant",
        content=assistant_response,
        sources=[s.model_dump() for s in sources],
    )
    session.add(assistant_msg)
    
    await session.commit()
    
    # 估算 token 使用量
    prompt_tokens = sum(len(m["content"]) // 4 for m in messages)
    completion_tokens = len(assistant_response) // 4
    
    return ChatCompletionResponse(
        id=response_id,
        conversation_id=conversation.id,
        kb_id=request.kb_id,
        choices=[
            ChatChoice(
                index=0,
                message=MessageCreate(
                    role="assistant",
                    content=assistant_response,
                ),
                finish_reason="stop",
            )
        ],
        sources=sources,
        usage=ChatUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
        created_at=assistant_msg.created_at,
    )


@router.post("/completions/stream")
async def create_chat_completion_stream(
    request: ChatCompletionRequest,
    session: AsyncSession = Depends(get_session),
):
    """创建对话补全（流式响应 SSE）"""
    import time
    
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
    
    # 保存用户消息
    user_msg = Message(
        id=str(uuid.uuid4()),
        conv_id=conversation.id,
        role="user",
        content=user_message_content,
    )
    session.add(user_msg)
    await session.commit()
    
    # ========== RAG 核心逻辑 ==========
    
    # 1. 检索相关内容
    retrieval_service = RetrievalService(session)
    search_results = await retrieval_service.search(
        kb_id=request.kb_id,
        query=user_message_content,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
    )
    
    # 2. 构建 RAG 提示词
    contexts = [
        {
            "content": r["content"],
            "doc_name": r.get("doc_name", "Unknown"),
            "doc_id": r["doc_id"],
            "chunk_id": r["chunk_id"],
            "score": r["score"],
            "page": r.get("metadata", {}).get("page", "N/A"),
        }
        for r in search_results
    ]
    
    rag_prompt = build_rag_prompt(user_message_content, contexts)
    
    # 3. 构建消息列表
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    
    # 添加历史消息
    if request.conversation_id:
        msg_result = await session.execute(
            select(Message)
            .where(Message.conv_id == request.conversation_id)
            .order_by(Message.created_at)
        )
        history_messages = msg_result.scalars().all()
        
        max_history = 10
        history_messages = history_messages[-max_history:] if len(history_messages) > max_history else history_messages
        
        for msg in history_messages:
            if msg.role != "user":  # 跳过刚保存的用户消息
                messages.append({
                    "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                    "content": msg.content,
                })
    
    messages.append({"role": "user", "content": rag_prompt})
    
    # 构建来源引用
    sources = [
        SourceReference(
            chunk_id=ctx["chunk_id"],
            doc_id=ctx["doc_id"],
            doc_name=ctx["doc_name"],
            content=ctx["content"][:500],
            score=ctx["score"],
            metadata={"page": ctx.get("page")},
        )
        for ctx in contexts
    ]
    
    async def generate_sse():
        """生成 SSE 流式响应"""
        llm = get_llm()
        response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
        created_timestamp = int(time.time())
        
        # 发送来源信息
        sources_event = {
            "id": response_id,
            "object": "chat.completion.sources",
            "conversation_id": conversation.id,
            "sources": [s.model_dump() for s in sources],
        }
        yield f"event: sources\ndata: {json.dumps(sources_event, ensure_ascii=False)}\n\n"
        
        # 发送开始事件
        start_event = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": created_timestamp,
            "model": "qwen-plus",
            "choices": [{
                "index": 0,
                "delta": {"role": "assistant"},
                "finish_reason": None,
            }],
        }
        yield f"data: {json.dumps(start_event, ensure_ascii=False)}\n\n"
        
        # 流式生成内容
        full_content = ""
        try:
            async for chunk in llm.generate_stream(
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                full_content += chunk
                
                # 发送内容块
                content_event = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created_timestamp,
                    "model": "qwen-plus",
                    "choices": [{
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": None,
                    }],
                }
                yield f"data: {json.dumps(content_event, ensure_ascii=False)}\n\n"
        
        except Exception as e:
            # 发送错误事件
            error_event = {
                "id": response_id,
                "object": "chat.completion.error",
                "error": {"message": str(e), "type": "generation_error"},
            }
            yield f"event: error\ndata: {json.dumps(error_event, ensure_ascii=False)}\n\n"
            return
        
        # 发送结束事件
        end_event = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": created_timestamp,
            "model": "qwen-plus",
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop",
            }],
        }
        yield f"data: {json.dumps(end_event, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        
        # 保存助手消息
        async with async_session_maker() as save_session:
            assistant_msg = Message(
                id=str(uuid.uuid4()),
                conv_id=conversation.id,
                role="assistant",
                content=full_content,
                sources=[s.model_dump() for s in sources],
            )
            save_session.add(assistant_msg)
            await save_session.commit()
    
    # 导入 async_session_maker
    from app.database import async_session_maker
    
    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
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
