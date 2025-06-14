"""
Problem management API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import Problem, ProblemCreate
from app.services.problem.crud import ProblemCRUD, get_problem_crud

router = APIRouter()

@router.get("/", response_model=List[Problem])
async def get_problems(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    difficulty: Optional[int] = Query(None, ge=1, le=5),
    tags: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    crud: ProblemCRUD = Depends(get_problem_crud)
):
    """
    問題一覧を取得
    
    - **skip**: スキップする件数
    - **limit**: 取得する件数
    - **difficulty**: 難易度フィルタ
    - **tags**: タグフィルタ
    """
    return await crud.get_problems(db, skip=skip, limit=limit, difficulty=difficulty, tags=tags)

@router.get("/{problem_id}", response_model=Problem)
async def get_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    crud: ProblemCRUD = Depends(get_problem_crud)
):
    """問題を取得"""
    problem = await crud.get_problem(db, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@router.post("/", response_model=Problem)
async def create_problem(
    problem: ProblemCreate,
    db: Session = Depends(get_db),
    crud: ProblemCRUD = Depends(get_problem_crud)
):
    """問題を作成"""
    return await crud.create_problem(db, problem)

@router.delete("/{problem_id}")
async def delete_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    crud: ProblemCRUD = Depends(get_problem_crud)
):
    """問題を削除"""
    success = await crud.delete_problem(db, problem_id)
    if not success:
        raise HTTPException(status_code=404, detail="Problem not found")
    return {"message": "Problem deleted successfully"}