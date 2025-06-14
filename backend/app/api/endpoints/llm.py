"""
LLM API endpoints for paraphrasing and explanation
"""

from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ParaphraseRequest, ParaphraseResponse, ExplainRequest, ExplainResponse
from app.services.llm.service import LLMService, get_llm_service

router = APIRouter()

@router.post("/paraphrase", response_model=ParaphraseResponse)
async def paraphrase_text(
    request: ParaphraseRequest,
    llm_service: LLMService = Depends(get_llm_service)
) -> ParaphraseResponse:
    """
    テキストをパラフレーズする
    
    - **text**: パラフレーズするテキスト
    - **creativity**: 創造性レベル (0.0-1.0)
    """
    try:
        return await llm_service.paraphrase(request.text, request.creativity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Paraphrase failed: {str(e)}")

@router.post("/explain", response_model=ExplainResponse)
async def explain_problem(
    request: ExplainRequest,
    llm_service: LLMService = Depends(get_llm_service)
) -> ExplainResponse:
    """
    問題の解説を生成する
    
    - **question**: 問題文
    - **answer**: 正解
    - **context**: 追加コンテキスト (省略可)
    """
    try:
        return await llm_service.generate_explanation(request.question, request.answer, request.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")