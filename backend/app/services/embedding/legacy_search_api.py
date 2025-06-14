"""
FastAPI類似検索エンドポイント実装

エンドポイント:
    GET /search?q=<query>&k=5
"""

import time
from typing import List, Optional, Dict, Any
import logging

from fastapi import FastAPI, Query, HTTPException, Depends
from pydantic import BaseModel, Field
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Response Models
class SearchResult(BaseModel):
    id: str = Field(description="問題ID")
    score: float = Field(description="類似度スコア (0-1)")
    snippet: str = Field(description="問題文のスニペット")
    difficulty: Optional[int] = Field(None, description="難易度")
    tags: Optional[str] = Field(None, description="タグ")

class SearchResponse(BaseModel):
    query: str = Field(description="検索クエリ")
    results: List[SearchResult] = Field(description="検索結果")
    total_time_ms: float = Field(description="検索時間 (ミリ秒)")
    k: int = Field(description="取得件数")

# Singleton pattern for models
class EmbeddingService:
    _instance = None
    _chroma_client = None
    _embedding_model = None
    _collection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(
        self, 
        chroma_path: str = "./data/chroma",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """サービス初期化 (アプリ起動時に1回だけ実行)"""
        if self._chroma_client is None:
            logger.info("Initializing ChromaDB client...")
            self._chroma_client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            try:
                self._collection = self._chroma_client.get_collection("problems")
                logger.info(f"Connected to 'problems' collection: {self._collection.count()} documents")
            except Exception as e:
                logger.error(f"Failed to get 'problems' collection: {e}")
                raise HTTPException(
                    status_code=500, 
                    detail="ChromaDB collection 'problems' not found. Run ingest_embeddings.py first."
                )
        
        if self._embedding_model is None:
            logger.info(f"Loading embedding model: {model_name}")
            self._embedding_model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully")
    
    def search_similar(self, query: str, k: int = 5) -> Dict[str, Any]:
        """類似検索実行"""
        if self._collection is None or self._embedding_model is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        
        start_time = time.time()
        
        try:
            # クエリのEmbedding生成
            query_embedding = self._embedding_model.encode([query]).tolist()[0]
            
            # ChromaDBで類似検索
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=['metadatas', 'documents', 'distances']
            )
            
            # 結果をフォーマット
            search_results = []
            if results['ids'] and results['ids'][0]:  # 結果が存在する場合
                for i, doc_id in enumerate(results['ids'][0]):
                    # Chromaのdistanceは小さいほど類似 -> scoreは大きいほど類似に変換
                    distance = results['distances'][0][i]
                    score = max(0.0, 1.0 - distance)  # distanceを0-1のscoreに変換
                    
                    metadata = results['metadatas'][0][i]
                    snippet = metadata.get('snippet', results['documents'][0][i][:150] + "...")
                    
                    search_results.append(SearchResult(
                        id=doc_id,
                        score=round(score, 4),
                        snippet=snippet,
                        difficulty=metadata.get('difficulty'),
                        tags=metadata.get('tags')
                    ))
            
            total_time_ms = round((time.time() - start_time) * 1000, 2)
            
            return SearchResponse(
                query=query,
                results=search_results,
                total_time_ms=total_time_ms,
                k=k
            )
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# FastAPIアプリ
app = FastAPI(
    title="G検定問題検索API",
    description="ChromaDBを使った問題文類似検索",
    version="1.0.0"
)

# サービスインスタンス
embedding_service = EmbeddingService()

@app.on_event("startup")
async def startup_event():
    """アプリ起動時にEmbeddingサービスを初期化"""
    try:
        embedding_service.initialize()
        logger.info("Embedding service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize embedding service: {e}")
        raise

def get_embedding_service() -> EmbeddingService:
    """Dependency injection用"""
    return embedding_service

@app.get("/search", response_model=SearchResponse, tags=["検索"])
async def search_problems(
    q: str = Query(..., description="検索クエリ", min_length=1),
    k: int = Query(5, description="取得件数", ge=1, le=50),
    service: EmbeddingService = Depends(get_embedding_service)
) -> SearchResponse:
    """
    問題文の類似検索を実行
    
    - **q**: 検索したいキーワードまたは文章
    - **k**: 取得する類似問題の件数 (1-50)
    
    レスポンス例:
    ```json
    {
        "query": "ニューラルネットワーク",
        "results": [
            {
                "id": "123",
                "score": 0.8542,
                "snippet": "ニューラルネットワークにおいて...",
                "difficulty": 2,
                "tags": "機械学習,深層学習"
            }
        ],
        "total_time_ms": 45.2,
        "k": 5
    }
    ```
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    logger.info(f"Search request: q='{q}', k={k}")
    return service.search_similar(q.strip(), k)

@app.get("/health", tags=["ヘルスチェック"])
async def health_check():
    """サービスヘルスチェック"""
    try:
        collection = embedding_service._collection
        if collection is None:
            raise Exception("Collection not initialized")
        
        count = collection.count()
        return {
            "status": "healthy",
            "collection_count": count,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/", tags=["情報"])
async def root():
    """API情報"""
    return {
        "service": "G検定問題検索API",
        "version": "1.0.0",
        "endpoints": {
            "search": "GET /search?q=<query>&k=<count>",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }

# デバッグ用: 直接実行時のサーバー起動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "search_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )