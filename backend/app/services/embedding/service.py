"""
Embedding service for similarity search
"""

import time
import logging
from typing import Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from fastapi import HTTPException

from app.core.config import settings
from app.models.schemas import SearchResponse, SearchResult

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Singleton embedding service for ChromaDB and sentence transformers"""
    
    _instance = None
    _chroma_client = None
    _embedding_model = None
    _collection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(
        self,
        chroma_path: str = None,
        model_name: str = None
    ):
        """Initialize ChromaDB and embedding model"""
        chroma_path = chroma_path or settings.CHROMA_PATH
        model_name = model_name or settings.EMBEDDING_MODEL
        
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
                    detail="ChromaDB collection 'problems' not found. Run embedding ingestion first."
                )
        
        if self._embedding_model is None:
            logger.info(f"Loading embedding model: {model_name}")
            self._embedding_model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully")
    
    async def search_similar(self, query: str, k: int = 5) -> SearchResponse:
        """Execute similarity search"""
        if self._collection is None or self._embedding_model is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        
        start_time = time.time()
        
        try:
            # Generate query embedding
            query_embedding = self._embedding_model.encode([query]).tolist()[0]
            
            # Search in ChromaDB
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=['metadatas', 'documents', 'distances']
            )
            
            # Format results
            search_results = []
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    score = max(0.0, 1.0 - distance)  # Convert distance to similarity score
                    
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

# Global instance
_embedding_service = EmbeddingService()

async def get_embedding_service() -> EmbeddingService:
    """Dependency injection for FastAPI"""
    if _embedding_service._chroma_client is None:
        await _embedding_service.initialize()
    return _embedding_service