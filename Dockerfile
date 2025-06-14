FROM python:3.11-slim

# システム依存関係
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ
WORKDIR /app

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY ingest_embeddings.py .
COPY search_api.py .

# データディレクトリ作成
RUN mkdir -p /app/data /app/cache

# モデルキャッシュの事前ダウンロード (ビルド時)
ENV TRANSFORMERS_CACHE=/app/cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# 権限設定
RUN chmod +x ingest_embeddings.py

# ヘルスチェック用
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ポート公開
EXPOSE 8000

# デフォルトコマンド
CMD ["uvicorn", "search_api:app", "--host", "0.0.0.0", "--port", "8000"]