"""
Main API v1 router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import search, exam, llm, problems

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(search.router, prefix="/search", tags=["検索"])
api_router.include_router(exam.router, prefix="/exam", tags=["模試"])
api_router.include_router(llm.router, prefix="/llm", tags=["LLM"])
api_router.include_router(problems.router, prefix="/problems", tags=["問題管理"])