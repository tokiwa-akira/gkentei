# G検定対策ツール - 開発環境セットアップガイド

## 📋 システム要件

- **OS**: Windows 10/11, macOS 12+, または Ubuntu 20.04+
- **RAM**: 最低 8GB（推奨 16GB以上）
- **ストレージ**: 最低 10GB の空き容量
- **CPU**: x64 アーキテクチャ（Apple Silicon対応）

## 🛠️ 必要なツールのインストール

### 1. Python (3.11以上)

#### Windows
```powershell
# Windows Package Manager (winget) を使用
winget install Python.Python.3.11

# または公式サイトからダウンロード
# https://www.python.org/downloads/windows/
```

#### macOS
```bash
# Homebrew を使用
brew install python@3.11

# または公式インストーラー
# https://www.python.org/downloads/mac-osx/
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### 2. UV (高速Pythonパッケージマネージャー)

#### 全プラットフォーム
```bash
# 公式インストーラー
curl -LsSf https://astral.sh/uv/install.sh | sh

# またはpipを使用
pip install uv
```

#### Windows (PowerShell)
```powershell
# PowerShell版
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 確認
```bash
uv --version
```

### 3. Node.js (18以上)

#### Windows
```powershell
# Node Version Manager (nvm) 推奨
winget install CoreyButler.NVMforWindows
nvm install 18
nvm use 18
```

#### macOS
```bash
# nvm を使用
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# または Homebrew
brew install node@18
```

#### Ubuntu/Debian
```bash
# NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# または nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

### 4. Docker & Docker Compose

#### Windows
```powershell
# Docker Desktop をインストール
winget install Docker.DockerDesktop
```

#### macOS
```bash
# Docker Desktop をインストール
brew install --cask docker
```

#### Ubuntu/Debian
```bash
# Docker Engine をインストール
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose をインストール
sudo apt-get install docker-compose-plugin

# ユーザーをdockerグループに追加
sudo usermod -aG docker $USER
```

### 5. Git

#### Windows
```powershell
winget install Git.Git
```

#### macOS
```bash
# Xcode Command Line Tools に含まれている
xcode-select --install

# または Homebrew
brew install git
```

#### Ubuntu/Debian
```bash
sudo apt install git
```

### 6. 推奨エディター・IDE

#### Visual Studio Code
```bash
# Windows
winget install Microsoft.VisualStudioCode

# macOS
brew install --cask visual-studio-code

# Ubuntu/Debian
sudo snap install code --classic
```

#### VSCode 推奨拡張機能
```bash
# 拡張機能を一括インストール
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort
code --install-extension bradlc.vscode-tailwindcss
code --install-extension esbenp.prettier-vscode
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension ms-vscode-remote.remote-containers
```

## 🚀 プロジェクトセットアップ

### 1. リポジトリのクローン
```bash
git clone https://github.com/your-username/g-kentei.git
cd g-kentei
```

### 2. バックエンド環境セットアップ
```bash
# プロジェクトディレクトリで
cd backend

# UV で仮想環境を作成・有効化
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows

# 依存関係をインストール
uv pip install -e ".[dev]"

# Playwright ブラウザをインストール
playwright install
```

### 3. フロントエンド環境セットアップ
```bash
cd frontend

# 依存関係をインストール
npm install

# または pnpm を使用（推奨）
npm install -g pnpm
pnpm install
```

### 4. 必要なディレクトリを作成
```bash
# プロジェクトルートで
mkdir -p data/{chroma,backups} cache models
```

### 5. 環境変数設定
```bash
# backend/.env ファイルを作成
cp backend/.env.example backend/.env
# 必要に応じて設定を編集
```

## 🗄️ データベースセットアップ

### 1. データベース初期化
```bash
cd backend

# Alembic マイグレーション実行
uv run alembic upgrade head
```

### 2. サンプルデータ（オプション）
```bash
# サンプル問題データがある場合
cp path/to/sample/problems.db data/problems.db
```

## 🤖 LLMモデルのセットアップ（オプション）

### 1. モデルダウンロード
```bash
# モデルダウンロードスクリプトを実行
./scripts/download_models.sh

# または手動でダウンロード
# ELYZA-japanese-Llama-2-7b-fast-instruct-q4_K_M.gguf を models/ に配置
```

## ✅ 動作確認

### 1. バックエンドサーバー起動
```bash
cd backend
uv run uvicorn app.main:app --reload
# http://localhost:8000/docs でAPI文書確認
```

### 2. フロントエンドサーバー起動
```bash
cd frontend
npm run dev
# http://localhost:3000 でアプリ確認
```

### 3. Docker Compose での確認
```bash
# プロジェクトルートで
docker compose -f docker-compose.new.yml up --build
```

## 🧪 テスト実行

### バックエンドテスト
```bash
cd backend
uv run pytest tests/ -v
```

### フロントエンドテスト
```bash
cd frontend
npm test
```

### 型チェック
```bash
# Backend
cd backend && uv run mypy app/

# Frontend
cd frontend && npm run type-check
```

## 🔧 開発ツール設定

### Pre-commit フック設定
```bash
cd backend
uv run pre-commit install
```

### Linting & Formatting
```bash
# Backend
cd backend
uv run black app/
uv run isort app/
uv run flake8 app/

# Frontend
cd frontend
npm run lint
npm run lint:fix
```

## 🐛 トラブルシューティング

### よくある問題と解決法

#### UV がインストールできない
```bash
# Python で直接インストール
pip install uv
```

#### Playwright ブラウザが見つからない
```bash
# ブラウザを再インストール
playwright install --force
```

#### Docker ビルドエラー
```bash
# キャッシュをクリア
docker system prune -a
docker compose -f docker-compose.new.yml build --no-cache
```

#### ポート競合エラー
```bash
# 使用中のポートを確認
netstat -tulpn | grep :8000  # Linux
lsof -i :8000               # macOS
netstat -ano | findstr :8000 # Windows

# プロセスを終了するか、別のポートを使用
```

#### Node.js バージョン問題
```bash
# 正しいバージョンを使用
nvm use 18
```

## 📚 追加リソース

- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)
- [React ドキュメント](https://react.dev/)
- [UV ドキュメント](https://docs.astral.sh/uv/)
- [Docker ドキュメント](https://docs.docker.com/)
- [Mantine UI ドキュメント](https://mantine.dev/)

## 🆘 サポート

問題が発生した場合：
1. このガイドのトラブルシューティングセクションを確認
2. [Issues](https://github.com/your-username/g-kentei/issues) で既存の問題を検索
3. 新しい Issue を作成（エラーメッセージとシステム情報を含む）

---

**セットアップ完了後**: `README_MIGRATION.md` で開発ワークフローを確認してください。