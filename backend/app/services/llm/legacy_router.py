"""
LLM Router for Paraphrasing API
G検定対策ツール用のパラフレーズエンドポイント
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import asyncio
import logging
from llama_cpp import Llama
import threading
import time

# ロガー設定
logger = logging.getLogger(__name__)

# リクエスト/レスポンスモデル
class ParaphraseRequest(BaseModel):
    text: str = Field(..., max_length=500, description="パラフレーズ対象のテキスト")
    max_length: Optional[int] = Field(120, ge=50, le=300, description="出力の最大文字数")
    temperature: Optional[float] = Field(0.3, ge=0.1, le=1.0, description="生成の多様性")

class ParaphraseResponse(BaseModel):
    paraphrased: str = Field(..., description="パラフレーズされたテキスト")
    original_length: int = Field(..., description="元テキストの文字数")
    paraphrased_length: int = Field(..., description="パラフレーズ後の文字数")
    processing_time_ms: int = Field(..., description="処理時間（ミリ秒）")

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: Optional[str] = None

# グローバルなLlamaインスタンス
llm_instance: Optional[Llama] = None
model_loading = False
model_load_lock = threading.Lock()

# FastAPIルーター
router = APIRouter(prefix="/llm", tags=["LLM"])

def create_paraphrase_prompt(text: str, max_length: int = 120) -> str:
    """パラフレーズ用のプロンプトを生成"""
    return f"""次の日本語テキストの意味を変えず表現を変えてください。単語の順序・語彙を変えても構いません。

要求:
- 元の意味を正確に保持する
- 文体や表現を変える
- {max_length}字以内で出力
- 改行や余計な説明は不要

元テキスト: {text}

パラフレーズ結果:"""

async def load_llm_model(model_path: str = "models/Llama-3-ELYZA-JP-8B-Q4_K_M.gguf") -> bool:
    """LLMモデルを非同期でロード"""
    global llm_instance, model_loading
    
    with model_load_lock:
        if llm_instance is not None:
            return True
            
        if model_loading:
            # 他のスレッドが既にロード中
            return False
            
        model_loading = True
    
    try:
        logger.info(f"Loading LLM model from {model_path}")
        start_time = time.time()
        
        # CPUでの推論に最適化された設定
        llm_instance = Llama(
            model_path=model_path,
            n_ctx=2048,        # コンテキスト長
            n_batch=512,       # バッチサイズ
            n_threads=4,       # CPUスレッド数
            verbose=False,     # ログ抑制
            use_mmap=True,     # メモリマップ使用
            use_mlock=False,   # メモリロック無効
        )
        
        load_time = time.time() - start_time
        logger.info(f"Model loaded successfully in {load_time:.2f}s")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False
    finally:
        model_loading = False

def extract_paraphrased_text(generated_text: str, original_text: str) -> str:
    """生成されたテキストからパラフレーズ部分を抽出"""
    # プロンプトの後の部分を取得
    if "パラフレーズ結果:" in generated_text:
        result = generated_text.split("パラフレーズ結果:")[-1].strip()
    else:
        result = generated_text.strip()
    
    # 改行を削除
    result = result.replace('\n', '').replace('\r', '')
    
    # 元テキストと同じ場合は失敗とみなす
    if result == original_text or not result:
        return ""
    
    return result

@router.on_event("startup")
async def startup_event():
    """アプリケーション起動時にモデルをロード"""
    await load_llm_model()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """LLMサービスのヘルスチェック"""
    return HealthResponse(
        status="healthy" if llm_instance is not None else "model_not_loaded",
        model_loaded=llm_instance is not None,
        model_path="models/Llama-3-ELYZA-JP-8B-Q4_K_M.gguf" if llm_instance else None
    )

@router.post("/paraphrase", response_model=ParaphraseResponse)
async def paraphrase_text(request: ParaphraseRequest):
    """テキストをパラフレーズする"""
    start_time = time.time()
    
    # モデルがロードされていない場合は自動ロード
    if llm_instance is None:
        if not await load_llm_model():
            raise HTTPException(
                status_code=503, 
                detail="LLM model is not available. Please check model file."
            )
    
    try:
        # プロンプト生成
        prompt = create_paraphrase_prompt(request.text, request.max_length)
        
        # LLM実行（非同期処理）
        def run_llm():
            return llm_instance(
                prompt,
                max_tokens=request.max_length + 50,  # 余裕を持たせる
                temperature=request.temperature,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["元テキスト:", "\n\n"],  # 停止条件
                echo=False
            )
        
        # 別スレッドで実行して非同期化
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_llm)
        
        # 結果からパラフレーズテキストを抽出
        generated_text = result["choices"][0]["text"]
        paraphrased = extract_paraphrased_text(generated_text, request.text)
        
        if not paraphrased:
            raise HTTPException(
                status_code=422,
                detail="Failed to generate meaningful paraphrase. Please try again."
            )
        
        # 文字数制限チェック
        if len(paraphrased) > request.max_length:
            paraphrased = paraphrased[:request.max_length] + "..."
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return ParaphraseResponse(
            paraphrased=paraphrased,
            original_length=len(request.text),
            paraphrased_length=len(paraphrased),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Paraphrase generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during paraphrase generation: {str(e)}"
        )

@router.post("/reload-model")
async def reload_model():
    """モデルを再ロードする（開発用）"""
    global llm_instance
    llm_instance = None
    
    success = await load_llm_model()
    if success:
        return {"status": "success", "message": "Model reloaded successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to reload model")

# テスト用のエンドポイント
@router.post("/test-paraphrase")
async def test_paraphrase():
    """API動作テスト用のエンドポイント"""
    test_text = "人工知能は機械学習と深層学習の技術を用いて、複雑な問題を解決する能力を持っています。"
    
    request = ParaphraseRequest(text=test_text)
    return await paraphrase_text(request)