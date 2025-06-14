"""
alembic/env.py への追加・変更点
既存のenv.pyに以下の変更を適用してください
"""

# 追加インポート（ファイル上部に追加）
import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# モデルのインポート（既存のインポートセクションに追加）
from models import Base

# target_metadataの設定（既存の行を置き換え）
target_metadata = Base.metadata

# run_migrations_online関数内の変更（既存の関数を以下で置き換え）
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # データディレクトリの作成
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # 設定からURLを取得、環境変数で上書き可能
    database_url = config.get_main_option("sqlalchemy.url")
    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./data/g_exam.db")

    connectable = engine_from_config(
        {"sqlalchemy.url": database_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # SQLiteでForeign Key制約を有効化
            render_as_batch=True,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()