# G検定対策ツール - Backend API

G検定対策ツールのバックエンドAPIサーバーです。

## 機能

- FastAPIベースのRESTful API
- SQLiteデータベースによる問題管理
- ChromaDBによるベクトル検索
- LLMによる問題生成・評価
- 模試生成機能

## 技術スタック

- Python 3.11+
- FastAPI
- SQLAlchemy
- ChromaDB
- PyTorch
- Transformers
- Llama.cpp

## 開発環境のセットアップ

1. 依存関係のインストール:
   ```bash
   uv sync --all-extras
   ```

2. データベースのマイグレーション:
   ```bash
   uv run alembic upgrade head
   ```

3. 開発サーバーの起動:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

## ライセンス

MIT License 