# G検定対策ツール

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)

**完全オフライン対応のG検定学習支援システム**

類似検索 • 模試生成 • 学習分析 • LLMパラフレーズ

</div>

## ✨ 特徴

- 🔍 **セマンティック検索**: ChromaDB + sentence-transformersによる高精度な問題検索
- 📝 **自動模試生成**: 難易度バランスを考慮した模試の自動作成
- 🤖 **LLMパラフレーズ**: ローカルLLMによる問題文の言い換え・解説生成
- 📊 **学習分析**: 詳細な学習統計とダッシュボード
- 🌐 **PWA対応**: オフライン動作可能なプログレッシブWebアプリ
- 🎨 **モダンUI**: Mantine UIによる美しく使いやすいインターフェース

## 🏗️ アーキテクチャ

```
┌─────────────────┐    HTTP/JSON    ┌──────────────────┐
│   React PWA     │ ─────────────── │   FastAPI        │
│   (Frontend)    │                 │   Backend        │
└─────────────────┘                 └──────────────────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        ▼                    ▼                    ▼
               ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
               │ SentenceTransf. │  │   ChromaDB      │  │   SQLite        │
               │ (all-MiniLM)    │  │   (Vector)      │  │   (Metadata)    │
               └─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 🚀 クイックスタート

### Docker Compose（推奨）
```bash
git clone https://github.com/tokiwa-akira/gkentei.git
cd g-kentei
docker compose up --build
```

### ローカル開発
```bash
# セットアップスクリプトを実行
./scripts/setup.sh

# または手動セットアップ
cd backend && uv sync --all-extras
cd ../frontend && npm install

# サーバー起動
cd backend && uv run uvicorn app.main:app --reload  # Backend: http://localhost:8000
cd frontend && npm run dev                          # Frontend: http://localhost:3000
```

詳細なインストール手順は [INSTALL.md](INSTALL.md) を参照してください。

## 📖 ドキュメント

- 📋 **[インストールガイド](INSTALL.md)** - 開発環境のセットアップ
- 🔄 **[マイグレーションガイド](README_MIGRATION.md)** - プロジェクト構造の変更点
- 🤖 **[Claude Code ガイド](CLAUDE.md)** - AI開発アシスタント向け情報
- 📚 **[API ドキュメント](http://localhost:8000/docs)** - FastAPI自動生成ドキュメント

## 🛠️ 技術スタック

### バックエンド
- **FastAPI** - 高性能なPython WebAPI フレームワーク
- **ChromaDB** - ベクトルデータベース
- **SQLite** - 軽量リレーショナルデータベース
- **sentence-transformers** - テキスト埋め込みモデル
- **llama-cpp-python** - ローカルLLM推論エンジン

### フロントエンド
- **React 18** - UIライブラリ
- **TypeScript** - 型安全なJavaScript
- **Vite** - 高速ビルドツール
- **Mantine** - UIコンポーネントライブラリ
- **Chart.js** - データ可視化

### DevOps
- **UV** - 高速Pythonパッケージマネージャー
- **Docker** - コンテナ化
- **GitHub Actions** - CI/CD
- **Playwright** - E2Eテスト

## 📊 主要機能

### 🔍 問題検索
- セマンティック類似検索
- フィルタリング（難易度・タグ）
- リアルタイム検索

### 📝 模試機能
- カスタム模試生成
- 難易度比率調整
- タイマー機能
- 結果分析

### 🤖 LLM機能
- 問題文パラフレーズ
- 自動解説生成
- コンテキスト理解

### 📈 学習分析
- 学習時間トラッキング
- 正答率分析
- 分野別統計
- 進捗可視化

## 🧪 テスト

```bash
# 全テスト実行
npm run test:all

# バックエンドテスト
cd backend && uv run pytest tests/ -v

# フロントエンドテスト
cd frontend && npm test

# E2Eテスト
cd backend && uv run playwright test
```

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## 📋 開発ロードマップ

- [x] ✅ **Phase 1**: コアアーキテクチャ構築
- [x] ✅ **Phase 2**: ベクトル検索システム
- [ ] 🔄 **Phase 3**: LLM統合・パラフレーズ機能
- [ ] 📅 **Phase 4**: フロントエンドUI完成
- [ ] 📅 **Phase 5**: 学習分析ダッシュボード
- [ ] 📅 **Phase 6**: PWA最適化・オフライン対応

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 🙏 謝辞

- [FastAPI](https://fastapi.tiangolo.com/) - 素晴らしいWebフレームワーク
- [ChromaDB](https://www.trychroma.com/) - オープンソースベクトルデータベース
- [Mantine](https://mantine.dev/) - 美しいReactコンポーネント
- [UV](https://github.com/astral-sh/uv) - 高速Pythonツールチェーン

## 📞 サポート

- 🐛 **バグレポート**: [Issues](https://github.com/tokiwa-akira/gkentei/issues)
- 💡 **機能要望**: [Feature Requests](https://github.com/tokiwa-akira/gkentei/issues/new?template=feature_request.md)
- ❓ **質問**: [Q&A Discussions](https://github.com/tokiwa-akira/gkentei/discussions)

---

<div align="center">
Made with ❤️ for G検定学習者
</div>