# G検定対策ツール - Webスクレイピング基盤

## 概要

Playwright を使用してWebページのHTMLを取得する、G検定対策ツール用のスクレイピング基盤です。

### 主な特徴

- ✅ **robots.txt 遵守**: 各サイトのクロール規則を自動チェック
- 🌐 **SPA 対応**: Playwright のヘッドレスChromeで JavaScript 完全実行
- ⏱️ **レート制限**: 1秒以上のウェイトで相手サーバーに配慮
- 📁 **整理された保存**: ドメイン別・日付別でファイル整理
- 🤖 **識別可能**: 専用User-Agentで正当なボット動作を明示

## インストール

### 必要な依存関係

```bash
pip install playwright requests
playwright install chromium
```

### ファイル配置

```
project/
├── scraper.py          # このスクレイパー
├── html/              # 取得したHTMLの保存先（自動作成）
│   ├── example.com/
│   ├── qiita.com/
│   └── ...
└── README_scraper.md  # このドキュメント
```

## 使用方法

### 基本的な使い方

```bash
python scraper.py <target_url>
```

### 実行例

```bash
# 基本的な記事ページ
python scraper.py https://qiita.com/someone/items/g-exam-study-tips

# G検定関連のブログ記事
python scraper.py https://example.com/blog/ai-basic-knowledge

# 企業の技術記事
python scraper.py https://tech.company.com/machine-learning-basics
```

### 実行時の出力例

```
🚀 スクレイピング開始: https://qiita.com/someone/items/g-exam-study-tips
📋 robots.txt をチェック中: https://qiita.com/robots.txt
✅ robots.txt: クロール許可
⏱️  レート制限: 1.00秒待機中...
🌐 HTMLを取得中: https://qiita.com/someone/items/g-exam-study-tips
✅ HTML取得完了 (45,231 文字)
💾 保存完了: html/qiita.com/2025-06-14_someone_items_g-exam-study-tips.html
🎉 スクレイピング完了!

📁 保存先: html/qiita.com/2025-06-14_someone_items_g-exam-study-tips.html
```

## 保存ファイルの命名規則

### ディレクトリ構造

```
html/
├── qiita.com/
│   ├── 2025-06-14_g-exam-tips.html
│   └── 2025-06-15_ai-study-guide.html
├── example.com/
│   ├── 2025-06-14_blog_machine-learning.html
│   └── 2025-06-14_index.html
└── tech-blog.company.com/
    └── 2025-06-14_articles_deep-learning.html
```

### ファイル名形式

```
{年-月-日}_{URLパス部分}.html
```

- 日付: `YYYY-MM-DD` 形式
- URLパス: スラッシュやピリオド以外は `_` に変換
- 長い場合: 先頭50文字まで

## エラーハンドリング

### robots.txt で禁止されている場合

```
📋 robots.txt をチェック中: https://example.com/robots.txt
❌ robots.txt: クロール禁止

❌ エラーが発生しました: robots.txt によりクロールが禁止されています
```

### ネットワークエラーの場合

```
❌ HTML取得失敗: net::ERR_NAME_NOT_RESOLVED

❌ エラーが発生しました: net::ERR_NAME_NOT_RESOLVED
```

## 設定カスタマイズ

### User-Agent の変更

```python
# scraper.py の __init__ メソッド内
self.user_agent = "Mozilla/5.0 (compatible; YourBot/1.0)"
```

### ウェイト時間の調整

```python
# より長いウェイト時間に変更
self.min_delay = 2.0  # 2秒間隔
```

### 保存先ディレクトリの変更

```python
# 保存先を変更
self.output_dir = Path("./scraped_data")
```

## 技術仕様

### 使用技術

- **Playwright**: ヘッドレスブラウザ自動化
- **Chromium**: JavaScript 実行エンジン
- **urllib.robotparser**: robots.txt 解析
- **asyncio**: 非同期処理

### User-Agent

```
Mozilla/5.0 (compatible; GExamBot/1.0)
```

### レート制限

- **最小間隔**: 1秒
- **適用方法**: 前回リクエストからの経過時間を計測

### タイムアウト設定

- **ページ読み込み**: 30秒
- **JavaScript待機**: 2秒追加

## ライセンス・注意事項

### robots.txt 遵守

本スクレイパーは各サイトの `robots.txt` を自動確認し、禁止されている場合は実行を停止します。

### 利用規約の確認

robots.txt をクリアしても、各サイトの利用規約やAI学習データ利用規則を別途確認してください。

### 商用利用の制限

取得したデータは **非商用・教育目的のみ** での利用を想定しています。

## トラブルシューティング

### Playwright のインストールエラー

```bash
# Chromium を手動で再インストール
playwright install chromium --force
```

### 権限エラー（Linux/Mac）

```bash
# 実行権限を付与
chmod +x scraper.py
```

### メモリ不足エラー

大きなページの場合、十分なメモリ（推奨16GB以上）を確保してください。

## 拡張予定

- [ ] 複数URL の一括処理
- [ ] 除外パターンの設定ファイル
- [ ] プロキシ対応
- [ ] 画像ダウンロード機能
- [ ] HTMLから問題文抽出の正規表現テンプレート