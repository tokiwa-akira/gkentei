"""
Search API endpoints
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from app.models.schemas import SearchResponse
from app.services.embedding.service import EmbeddingService, get_embedding_service

router = APIRouter()

@router.get("/", response_model=SearchResponse)
async def search_problems(
    q: str = Query(..., description="検索クエリ", min_length=1),
    k: int = Query(5, description="取得件数", ge=1, le=50),
    service: EmbeddingService = Depends(get_embedding_service)
) -> SearchResponse:
    """
    問題文の類似検索を実行
    
    - **q**: 検索したいキーワードまたは文章
    - **k**: 取得する類似問題の件数 (1-50)
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    return await service.search_similar(q.strip(), k)