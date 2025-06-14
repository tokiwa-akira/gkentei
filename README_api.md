# T-04: LLM Paraphrase API

## 概要

G検定対策ツール用のパラフレーズAPI。著作権に配慮し、問題文の意味を保持したまま表現を書き換えます。

## 技術仕様

- **エンジン**: llama-cpp-python + Llama-3-ELYZA-JP-8B-Q4
- **フレームワーク**: FastAPI
- **推論**: CPU最適化（GPU不要）
- **応答時間**: 1問あたり3-5秒（CPU 8コア想定）

## セットアップ

### 1. 依存関係インストール

```bash
pip install -r requirements.txt
```

### 2. モデルダウンロード

```bash
# モデルディレクトリ作成
mkdir -p models

# Llama-3-ELYZA-JP-8B-Q4をダウンロード
# ※実際のダウンロードURLは利用可能なソースに応じて調整
wget -O models/Llama-3-ELYZA-JP-8B-Q4_K_M.gguf \
  "https://huggingface.co/elyza/Llama-3-ELYZA-JP-8B-q4_k_m-gguf/resolve/main/llama-3-elyza-jp-8b-q4_k_m.gguf"
```

### 3. サーバー起動

```bash
python main.py
# または
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API エンドポイント

### 🔥 パラフレーズ生成

**エンドポイント**: `POST /llm/paraphrase`

**リクエスト例**:
```bash
curl -X POST "http://localhost:8000/llm/paraphrase" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "人工知能は機械学習と深層学習の技術を用いて、複雑な問題を解決する能力を持っています。",
    "max_length": 120,
    "temperature": 0.3
  }'
```

**レスポンス例**:
```json
{
  "paraphrased": "AIは機械学習および深層学習を活用し、複雑な課題に対処する能力があります。",
  "original_length": 42,
  "paraphrased_length": 38,
  "processing_time_ms": 3420
}
```

### 📊 ヘルスチェック

```bash
curl -X GET "http://localhost:8000/llm/health"
```

**レスポンス**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "models/Llama-3-ELYZA-JP-8B-Q4_K_M.gguf"
}
```

### 🔄 モデル再ロード（開発用）

```bash
curl -X POST "http://localhost:8000/llm/reload-model"
```

### 🧪 テスト実行

```bash
curl -X POST "http://localhost:8000/llm/test-paraphrase"
```

## パラメータ仕様

| パラメータ | 型 | デフォルト | 範囲 | 説明 |
|------------|-----|-----------|------|------|
| `text` | string | 必須 | 1-500文字 | パラフレーズ対象テキスト |
| `max_length` | int | 120 | 50-300 | 出力の最大文字数 |
| `temperature` | float | 0.3 | 0.1-1.0 | 生成の多様性（低い=保守的） |

## パフォーマンス最適化

### メモリ使用量
- **推定**: 4-6GB RAM（Q4量子化モデル）
- **推奨**: 8GB RAM以上

### CPU最適化設定
```python
# router_llm.py内の設定
n_threads=4        # CPUコア数に応じて調整
n_batch=512        # バッチサイズ
use_mmap=True      # メモリマップ使用
```

### Docker環境での制限
```yaml
deploy:
  resources:
    limits:
      memory: 8G
    reservations:
      memory: 4G
```

## トラブルシューティング

### モデルが読み込めない
```bash
# ファイル存在確認
ls -la models/Llama-3-ELYZA-JP-8B-Q4_K_M.gguf

# 権限確認
chmod 644 models/*.gguf
```

### メモリ不足エラー
- `n_batch`を256に減らす
- より小さいモデル（rinna-3.6B）を検討

### 生成品質が低い
- `temperature`を0.5-0.7に上げる
- プロンプトテンプレートを調整

## 品質保証

### 単体テスト例
```bash
# パラフレーズ精度テスト
python -m pytest tests/test_llm_router.py::test_paraphrase_quality

# 処理時間テスト  
python -m pytest tests/test_llm_router.py::test_response_time
```

### 受け入れ条件
- ✅ モデルロード時間 < 30秒
- ✅ 1問生成時間 < 5秒
- ✅ 意味保持率 > 70%（手動評価）
- ✅ レスポンス形式がAPI仕様準拠

## ライセンス

- **コード**: MIT License
- **モデル**: Llama-3-ELYZA-JP-8B ライセンスに準拠
- **生成テキスト**: 非商用・教育目的のみ