"""
LLM service for paraphrasing and explanation generation
"""

import time
import logging
from typing import Optional

from app.core.config import settings
from app.models.schemas import ParaphraseResponse, ExplainResponse

logger = logging.getLogger(__name__)

class LLMService:
    """Local LLM service for text generation tasks"""
    
    def __init__(self):
        self._model = None
        self._initialized = False
    
    async def initialize(self, model_path: Optional[str] = None):
        """Initialize LLM model"""
        try:
            # TODO: Initialize llama-cpp-python model
            # from llama_cpp import Llama
            # model_path = model_path or settings.LLM_MODEL_PATH
            # self._model = Llama(model_path=model_path)
            self._initialized = True
            logger.info("LLM service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    async def paraphrase(self, text: str, creativity: float = 0.7) -> ParaphraseResponse:
        """Generate paraphrased text"""
        start_time = time.time()
        
        # TODO: Implement actual paraphrasing with LLM
        # For now, return a placeholder
        paraphrased = f"[パラフレーズ] {text}"
        
        processing_time = (time.time() - start_time) * 1000
        
        return ParaphraseResponse(
            original=text,
            paraphrased=paraphrased,
            processing_time_ms=processing_time
        )
    
    async def generate_explanation(
        self, 
        question: str, 
        answer: str, 
        context: Optional[str] = None
    ) -> ExplainResponse:
        """Generate explanation for a problem"""
        start_time = time.time()
        
        # TODO: Implement actual explanation generation with LLM
        # For now, return a placeholder
        explanation = f"この問題は{answer}に関する内容です。詳細な解説はLLMモデルにより生成されます。"
        
        processing_time = (time.time() - start_time) * 1000
        
        return ExplainResponse(
            question=question,
            explanation=explanation,
            processing_time_ms=processing_time
        )

# Global instance
_llm_service = LLMService()

async def get_llm_service() -> LLMService:
    """Dependency injection for FastAPI"""
    if not _llm_service._initialized:
        await _llm_service.initialize()
    return _llm_service