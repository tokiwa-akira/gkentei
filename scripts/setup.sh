#!/bin/bash

# G検定対策ツール セットアップスクリプト

set -e

echo "🚀 G検定対策ツール セットアップを開始します..."

# 必要なディレクトリを作成
echo "📁 ディレクトリを作成中..."
mkdir -p data/{chroma,backups} cache models

# UV をチェック・インストール
echo "🔧 UV をチェック中..."
if ! command -v uv &> /dev/null; then
    echo "UV をインストール中..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Python依存関係をインストール
echo "🐍 Backend依存関係をインストール中..."
if [ -f "backend/pyproject.toml" ]; then
    cd backend
    uv sync --all-extras
    cd ..
else
    echo "⚠️  backend/pyproject.toml が見つかりません"
fi

# Node.js依存関係をインストール
echo "📦 Frontend依存関係をインストール中..."
if [ -f "frontend/package.json" ]; then
    cd frontend && npm install && cd ..
else
    echo "⚠️  frontend/package.json が見つかりません"
fi

# データベースマイグレーション
echo "🗄️  データベースマイグレーション実行中..."
if [ -f "backend/alembic.ini" ]; then
    cd backend && uv run alembic upgrade head && cd ..
else
    echo "⚠️  Alembic設定が見つかりません"
fi

# 初期データ確認
echo "📊 初期データを確認中..."
if [ ! -f "data/problems.db" ]; then
    echo "⚠️  問題データベースが見つかりません。data/problems.db を配置してください。"
fi

# モデルダウンロード確認
echo "🤖 LLMモデルを確認中..."
if [ ! -f "models/llama-3-elyza-jp-8b-q4.gguf" ]; then
    echo "⚠️  LLMモデルが見つかりません。"
    echo "   以下のコマンドでダウンロードできます:"
    echo "   ./scripts/download_models.sh"
fi

echo "✅ セットアップが完了しました！"
echo ""
echo "🎯 次のステップ:"
echo "1. データベースに問題データを追加"
echo "2. LLMモデルをダウンロード (オプション)"
echo "3. Embeddingを初期化: cd backend && uv run python app/scripts/init_embeddings.py"
echo "4. 開発サーバーを起動: cd frontend && npm run dev | cd backend && uv run uvicorn app.main:app --reload"
echo "   または Docker Compose: docker compose up --build"