"""
Exam generation API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ExamGenerateRequest, ExamResponse
from app.services.exam.generator import ExamGenerator, get_exam_generator

router = APIRouter()

@router.post("/generate", response_model=ExamResponse)
async def generate_exam(
    request: ExamGenerateRequest,
    generator: ExamGenerator = Depends(get_exam_generator)
) -> ExamResponse:
    """
    模試を生成する
    
    - **num_questions**: 問題数 (1-200)
    - **difficulty_ratio**: 難易度比率 (合計1.0)
    - **tags**: 対象タグ (省略時は全分野)
    - **time_limit_min**: 制限時間 (10-300分)
    """
    try:
        return await generator.generate_exam(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exam generation failed: {str(e)}")

@router.get("/results/{exam_id}")
async def get_exam_results(exam_id: str):
    """模試結果を取得"""
    # TODO: Implement exam results retrieval
    return {"exam_id": exam_id, "message": "Not implemented yet"}