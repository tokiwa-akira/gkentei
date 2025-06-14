# G検定対策ツール - Frontend

React + TypeScript ベースのプログレッシブ Web アプリ

## 🚀 クイックスタート

```bash
# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

## 📁 ディレクトリ構造

```
src/
├── components/    # React コンポーネント
├── pages/         # ページコンポーネント
├── hooks/         # カスタムフック
├── services/      # API クライアント
├── types/         # TypeScript 型定義
├── utils/         # ユーティリティ関数
└── styles/        # スタイリング
```

## 🔧 開発コマンド

```bash
# 開発サーバー起動
npm run dev

# ビルド
npm run build

# プレビュー
npm run preview

# テスト実行
npm test

# 型チェック
npm run type-check

# リンティング
npm run lint
npm run lint:fix
```

## 🎨 技術スタック

- **React 18** - UI ライブラリ
- **TypeScript** - 型安全性
- **Vite** - 高速ビルドツール
- **Mantine** - UI コンポーネントライブラリ
- **Chart.js** - データ可視化
- **Zustand** - 状態管理

## 🌐 PWA 機能

- オフライン対応
- インストール可能
- プッシュ通知 (将来実装予定)
- バックグラウンド同期 (将来実装予定)

## 🔗 API 連携

バックエンド API との通信は `src/services/` で管理されています。開発時は Vite のプロキシ機能により `http://localhost:8000` のバックエンドと自動連携します。