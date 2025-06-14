# main.py での統合例
"""
FastAPI メインアプリケーション
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# LLMルーターをインポート
from router_llm import router as llm_router

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリ初期化
app = FastAPI(
    title="G検定対策ツール API",
    description="オフライン学習支援システム",
    version="1.0.0"
)

# CORS設定（開発用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React開発サーバー
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLMルーターを登録
app.include_router(llm_router)

# ルートエンドポイント
@app.get("/")
async def root():
    return {"message": "G検定対策ツール API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "G検定対策API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 開発時のみ
        log_level="info"
    )