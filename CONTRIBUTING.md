# Contributing to G検定対策ツール

G検定対策ツールプロジェクトへの貢献をお考えいただき、ありがとうございます！このガイドでは、プロジェクトに効果的に貢献する方法について説明します。

## 🤝 貢献の方法

### 1. バグレポート
- [Issues](https://github.com/your-username/g-kentei/issues) でバグレポートを作成
- バグレポートテンプレートに従って詳細を記載
- 再現手順、環境情報、エラーメッセージを含める

### 2. 機能要望
- [Feature Request](https://github.com/your-username/g-kentei/issues/new?template=feature_request.md) を作成
- 機能の目的、ユースケース、実装案を説明

### 3. コードコントリビューション
- Fork → Branch → Commit → Pull Request の流れ
- コーディング規約に従う
- テストを追加・確認する

### 4. ドキュメント改善
- README、API ドキュメント、コメントの改善
- 翻訳、例文の追加

## 🔧 開発環境のセットアップ

### 前提条件
- Python 3.11+
- Node.js 18+
- UV (Python パッケージマネージャー)
- Git

### セットアップ手順
```bash
# 1. フォーク・クローン
git clone https://github.com/YOUR_USERNAME/g-kentei.git
cd g-kentei

# 2. セットアップスクリプト実行
./scripts/setup.sh

# 3. 開発サーバー起動
# ターミナル1: Backend
cd backend && uv run uvicorn app.main:app --reload

# ターミナル2: Frontend
cd frontend && npm run dev
```

## 📝 開発ワークフロー

### 1. ブランチ戦略
```bash
# メインブランチ
main        # 本番リリース用
develop     # 開発用統合ブランチ

# フィーチャーブランチ
feature/issue-123-add-search-filter
feature/dashboard-analytics
fix/embedding-memory-leak
docs/api-documentation
```

### 2. ブランチの作成
```bash
# develop ブランチから作業ブランチを作成
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 3. コミットメッセージ
```bash
# フォーマット: type(scope): description
feat(search): add semantic similarity search
fix(api): resolve memory leak in embedding service
docs(readme): update installation guide
test(exam): add unit tests for exam generation
style(frontend): fix ESLint warnings
refactor(backend): reorganize service layer
perf(search): optimize ChromaDB queries
chore(deps): update dependencies
```

### 4. Pull Request プロセス
1. **変更をコミット**
   ```bash
   git add .
   git commit -m "feat(search): add advanced filtering"
   git push origin feature/your-feature-name
   ```

2. **Pull Request 作成**
   - GitHub で Pull Request を作成
   - PR テンプレートに従って記載
   - 関連する Issue をリンク

3. **レビュー対応**
   - CI/CD チェックが通ることを確認
   - レビューアーのフィードバックに対応
   - 必要に応じてコミットを追加

4. **マージ**
   - レビュー承認後、maintainer がマージ
   - Squash and merge を使用

## 🧪 テスト

### バックエンドテスト
```bash
cd backend

# 全テスト実行
uv run pytest tests/ -v

# 特定のテスト
uv run pytest tests/test_search.py -v

# カバレッジ付き
uv run pytest tests/ --cov=app --cov-report=html

# 型チェック
uv run mypy app/

# Linting
uv run flake8 app/
uv run black --check app/
uv run isort --check-only app/
```

### フロントエンドテスト
```bash
cd frontend

# 単体テスト
npm test

# E2E テスト
npm run test:e2e

# 型チェック
npm run type-check

# Linting
npm run lint
```

### 統合テスト
```bash
# Docker Compose でフルスタックテスト
docker compose -f docker-compose.new.yml up --build
# 別ターミナルで
curl http://localhost:8000/health
curl http://localhost:3000
```

## 📏 コーディング規約

### Python (Backend)
```python
# Black フォーマッター設定 (88文字)
# isort でインポート整理
# flake8 でリンティング
# mypy で型チェック

# 例: app/services/example_service.py
from typing import List, Optional
import logging

from app.core.config import settings
from app.models.schemas import ExampleSchema

logger = logging.getLogger(__name__)

class ExampleService:
    """Example service class."""
    
    def __init__(self) -> None:
        self.config = settings
    
    async def process_data(self, data: List[str]) -> Optional[ExampleSchema]:
        """Process data and return result."""
        try:
            # 処理ロジック
            return ExampleSchema(...)
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return None
```

### TypeScript (Frontend)
```typescript
// Prettier + ESLint 設定
// 関数コンポーネント + hooks 使用

// 例: src/components/ExampleComponent.tsx
import { useState, useEffect } from 'react'
import { Button, Container } from '@mantine/core'
import { useExampleHook } from '@/hooks/useExample'
import type { ExampleProps } from '@/types/example'

export function ExampleComponent({ title, onSubmit }: ExampleProps) {
  const [loading, setLoading] = useState(false)
  const { data, error } = useExampleHook()

  const handleSubmit = async () => {
    setLoading(true)
    try {
      await onSubmit(data)
    } catch (err) {
      console.error('Submit failed:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container>
      <h2>{title}</h2>
      <Button onClick={handleSubmit} loading={loading}>
        Submit
      </Button>
    </Container>
  )
}
```

## 🔒 セキュリティ

### 報告方法
- 重大なセキュリティ問題は Issue ではなくメール報告
- セキュリティ報告用: [security@example.com]
- 報告内容: 影響範囲、再現手順、修正提案

### セキュリティガイドライン
- 外部データの適切なサニタイゼーション
- SQLインジェクション対策
- XSS防止
- 認証・認可の実装
- 秘密情報のログ出力禁止

## 📚 ドキュメント規約

### API ドキュメント
```python
@router.post("/search", response_model=SearchResponse)
async def search_problems(
    q: str = Query(..., description="検索クエリ", min_length=1),
    k: int = Query(5, description="取得件数", ge=1, le=50),
) -> SearchResponse:
    """
    問題文の類似検索を実行
    
    - **q**: 検索したいキーワードまたは文章
    - **k**: 取得する類似問題の件数 (1-50)
    
    Returns:
        SearchResponse: 検索結果と実行時間
    
    Raises:
        HTTPException: 検索に失敗した場合
    """
```

### コメント規約
```python
def complex_algorithm(data: List[str]) -> Dict[str, Any]:
    """
    複雑なアルゴリズムの実装
    
    Args:
        data: 処理対象のデータリスト
    
    Returns:
        処理結果を含む辞書
        
    Note:
        このアルゴリズムは O(n log n) の時間計算量
    """
    # ステップ1: データの前処理
    processed = preprocess_data(data)
    
    # ステップ2: メインアルゴリズム実行
    result = run_algorithm(processed)
    
    return result
```

## 🚀 リリースプロセス

### バージョニング
- セマンティックバージョニング (SemVer) を使用
- MAJOR.MINOR.PATCH (例: 1.2.3)

### リリース手順
1. **develop → main への PR 作成**
2. **バージョンタグ付け**
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
3. **GitHub Release 作成**
4. **Docker イメージビルド・プッシュ**

## ❓ よくある質問

### Q: 開発環境で ChromaDB が起動しない
A: `data/chroma` ディレクトリの権限を確認し、必要に応じて削除・再作成してください。

### Q: フロントエンドのビルドが失敗する
A: `node_modules` を削除して `npm install` を再実行してください。

### Q: テストが失敗する
A: 環境変数が正しく設定されているか確認し、テスト用データベースが初期化されているか確認してください。

## 📞 サポート

- 💬 **Discord**: [招待リンク]
- 📧 **Email**: [contact@example.com]
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/g-kentei/issues)
- 💡 **Discussions**: [GitHub Discussions](https://github.com/your-username/g-kentei/discussions)

---

## 🙏 謝辞

コントリビューターの皆様に感謝いたします。あなたの貢献がプロジェクトをより良いものにします！