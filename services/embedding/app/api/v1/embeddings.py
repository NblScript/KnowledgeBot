"""Embedding API 路由"""

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.schemas.embedding import (
    BatchEmbedRequest,
    BatchEmbedResponse,
    CollectionCreateRequest,
    CollectionInfo,
    DeleteResponse,
    EmbeddingData,
    HealthResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.services.embedding_service import get_embedding_service
from app.services.milvus_client import get_milvus_client

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    milvus_client = get_milvus_client()
    milvus_status = "connected" if milvus_client.is_connected() else "disconnected"
    
    return HealthResponse(
        status="healthy",
        service="embedding-service",
        milvus=milvus_status,
        version="1.0.0",
    )


@router.post("/texts", response_model=BatchEmbedResponse)
async def embed_texts(request: BatchEmbedRequest):
    """批量文本向量化
    
    将文本列表转换为向量表示
    """
    embedding_service = get_embedding_service()
    
    try:
        embeddings = await embedding_service.embed_texts(request.texts)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Embedding failed: {str(e)}",
        )
    
    # 构建响应
    data = [
        EmbeddingData(index=i, embedding=emb)
        for i, emb in enumerate(embeddings)
    ]
    
    # 计算估算的 token 数量
    total_chars = sum(len(text) for text in request.texts)
    estimated_tokens = total_chars // 4  # 粗略估算
    
    return BatchEmbedResponse(
        data=data,
        model=embedding_service.model_name,
        usage={
            "prompt_tokens": estimated_tokens,
            "total_tokens": estimated_tokens,
        },
    )


@router.post("/search", response_model=SearchResponse)
async def search_vectors(request: SearchRequest):
    """向量检索
    
    在指定集合中搜索相似内容
    """
    embedding_service = get_embedding_service()
    milvus_client = get_milvus_client()
    
    # 检查集合是否存在
    if not milvus_client.has_collection(request.collection_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection {request.collection_id} not found",
        )
    
    # 获取查询向量
    try:
        query_vector = await embedding_service.embed_single(request.query)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Embedding failed: {str(e)}",
        )
    
    # 执行向量检索
    try:
        results = milvus_client.search(
            collection_id=request.collection_id,
            query_vector=query_vector,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            filters=request.filters,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Vector search failed: {str(e)}",
        )
    
    # 构建响应
    search_results = [
        SearchResult(
            chunk_id=r["chunk_id"],
            doc_id=r["doc_id"],
            content=r["content"],
            score=r["score"],
            metadata=r.get("metadata"),
        )
        for r in results
    ]
    
    return SearchResponse(
        query=request.query,
        results=search_results,
        total=len(search_results),
    )


@router.post("/collections", response_model=CollectionInfo)
async def create_collection(request: CollectionCreateRequest):
    """创建向量集合
    
    为指定知识库创建 Milvus Collection
    """
    milvus_client = get_milvus_client()
    
    try:
        collection = milvus_client.create_collection(
            collection_id=request.collection_id,
            embedding_dim=request.embedding_dim,
        )
        
        return CollectionInfo(
            collection_id=request.collection_id,
            name=collection.name,
            embedding_dim=request.embedding_dim,
            exists=True,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create collection: {str(e)}",
        )


@router.get("/collections/{collection_id}", response_model=CollectionInfo)
async def get_collection_info(collection_id: str):
    """获取集合信息"""
    milvus_client = get_milvus_client()
    
    exists = milvus_client.has_collection(collection_id)
    
    if not exists:
        return CollectionInfo(
            collection_id=collection_id,
            name="",
            embedding_dim=0,
            exists=False,
        )
    
    collection = milvus_client.get_collection(collection_id)
    
    return CollectionInfo(
        collection_id=collection_id,
        name=collection.name,
        embedding_dim=settings.embedding_dim,
        exists=True,
    )


@router.delete("/collections/{collection_id}", response_model=DeleteResponse)
async def delete_collection(collection_id: str):
    """删除向量集合"""
    milvus_client = get_milvus_client()
    
    if not milvus_client.has_collection(collection_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection {collection_id} not found",
        )
    
    try:
        success = milvus_client.drop_collection(collection_id)
        return DeleteResponse(
            success=success,
            message=f"Collection {collection_id} deleted successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete collection: {str(e)}",
        )


