# GitHub リポジトリセットアップガイド

このガイドでは、G検定対策ツールのGitHubリポジトリを作成・設定する手順を説明します。

## 📋 前提条件

- GitHubアカウントを持っている
- Git がローカルにインストールされている
- SSH キーまたは Personal Access Token が設定済み

## 🚀 1. GitHubリポジトリの作成

### オプションA: GitHub Web UIで作成
1. [GitHub](https://github.com) にログイン
2. 右上の「+」→「New repository」をクリック
3. 以下の設定で作成:
   ```
   Repository name: g-kentei
   Description: G検定対策ツール - 完全オフライン対応の学習支援システム
   Visibility: Public (または Private)
   □ Add a README file (チェックしない)
   □ Add .gitignore (チェックしない)
   □ Choose a license (チェックしない)
   ```
4. 「Create repository」をクリック

### オプションB: GitHub CLI で作成
```bash
# GitHub CLI をインストール (未インストールの場合)
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Ubuntu: sudo apt install gh

# ログイン
gh auth login

# リポジトリ作成
cd /path/to/g-kentei
gh repo create g-kentei --public --description "G検定対策ツール - 完全オフライン対応の学習支援システム"
```

## 🔗 2. ローカルリポジトリとリモートの接続

```bash
# プロジェクトディレクトリに移動
cd /path/to/g-kentei

# Git 初期化 (まだの場合)
git init

# リモートリポジトリを追加
git remote add origin https://github.com/YOUR_USERNAME/g-kentei.git

# または SSH の場合
git remote add origin git@github.com:YOUR_USERNAME/g-kentei.git

# 現在のファイルをステージング
git add .

# 初回コミット
git commit -m "🎉 Initial commit: Modern G検定 study tool

- Modern backend structure with FastAPI
- React PWA frontend with TypeScript
- UV for Python package management
- Docker containerization
- Comprehensive documentation"

# メインブランチにプッシュ
git branch -M main
git push -u origin main
```

## ⚙️ 3. リポジトリ設定

### GitHub Settings の設定
1. リポジトリページで「Settings」タブをクリック
2. 以下の設定を行う:

#### General Settings
```
Repository name: g-kentei
Description: G検定対策ツール - 完全オフライン対応の学習支援システム
Website: (デプロイ後に追加)
Topics: g-exam, machine-learning, japanese, pwa, fastapi, react, education
```

#### Features
```
☑ Wikis
☑ Issues
☑ Sponsorships (オプション)
☑ Preserve this repository (オプション)
☑ Discussions
```

#### Pull Requests
```
☑ Allow merge commits
☑ Allow squash merging
☑ Allow rebase merging
☑ Always suggest updating pull request branches
☑ Allow auto-merge
☑ Automatically delete head branches
```

#### Security & analysis
```
☑ Dependency graph
☑ Dependabot alerts
☑ Dependabot security updates
☑ Private vulnerability reporting
```

### Branch Protection Rules
```bash
# GitHub CLI で設定する場合
gh api repos/YOUR_USERNAME/g-kentei/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["ci/backend-test","ci/frontend-test"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field restrictions=null
```

または Web UI で:
1. Settings > Branches
2. "Add rule" で `main` ブランチに以下のルールを設定:
   ```
   ☑ Require a pull request before merging
   ☑ Require approvals (1)
   ☑ Dismiss stale pull request approvals when new commits are pushed
   ☑ Require review from code owners
   ☑ Require status checks to pass before merging
   ☑ Require branches to be up to date before merging
   ☑ Require conversation resolution before merging
   ☑ Include administrators
   ```

## 🏷️ 4. Labels の設定

GitHub Issues で使用するラベルを作成:

```bash
# GitHub CLI でラベル作成
gh label create "bug" --description "Something isn't working" --color "d73a4a"
gh label create "enhancement" --description "New feature or request" --color "a2eeef"
gh label create "documentation" --description "Improvements or additions to documentation" --color "0075ca"
gh label create "good first issue" --description "Good for newcomers" --color "7057ff"
gh label create "help wanted" --description "Extra attention is needed" --color "008672"
gh label create "backend" --description "Backend related changes" --color "fef2c0"
gh label create "frontend" --description "Frontend related changes" --color "bfdadc"
gh label create "ci/cd" --description "Continuous Integration/Deployment" --color "f9d0c4"
gh label create "performance" --description "Performance improvements" --color "d4c5f9"
gh label create "security" --description "Security related" --color "b60205"
```

## 🔒 5. Secrets の設定

GitHub Actions で使用する秘密情報を設定:

1. Settings > Secrets and variables > Actions
2. 以下のシークレットを追加:

```
# Docker Hub (オプション)
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_password

# 本番デプロイ用 (将来)
PRODUCTION_SERVER_HOST=your_server_ip
PRODUCTION_SERVER_USER=deploy_user
PRODUCTION_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...

# 監視・分析ツール (オプション)
SENTRY_DSN=https://your_sentry_dsn
CODECOV_TOKEN=your_codecov_token
```

## 📊 6. GitHub Pages の設定 (ドキュメント用)

1. Settings > Pages
2. Source: "Deploy from a branch"
3. Branch: "main" / "docs" (ドキュメントブランチがある場合)
4. Folder: "/" または "/docs"

## 🏃‍♂️ 7. 初回 CI/CD の実行確認

```bash
# develop ブランチ作成
git checkout -b develop
git push -u origin develop

# CI/CD をトリガーするため、小さな変更をプッシュ
echo "# CI/CD Test" >> CI_TEST.md
git add CI_TEST.md
git commit -m "ci: test GitHub Actions workflow"
git push origin develop

# Pull Request 作成
gh pr create --title "ci: Test GitHub Actions setup" --body "Testing CI/CD pipeline configuration"
```

## 🔄 8. 継続的な管理

### 定期的なメンテナンス
- **Dependencies**: Dependabot の Pull Request を定期的にレビュー
- **Security**: Security alerts の対応
- **Issues**: コミュニティからのフィードバック対応
- **Releases**: 定期的なリリース (セマンティックバージョニング)

### チーム開発の場合
```bash
# コラボレーター追加 (GitHub CLI)
gh api repos/YOUR_USERNAME/g-kentei/collaborators/COLLABORATOR_USERNAME \
  --method PUT \
  --field permission="push"

# または Web UI で Settings > Collaborators and teams
```

## 📋 チェックリスト

設定完了後、以下を確認:

- [ ] リポジトリが正常に作成されている
- [ ] ローカルとリモートが同期されている
- [ ] GitHub Actions が正常に動作している
- [ ] Branch protection rules が設定されている
- [ ] Issues と PR テンプレートが利用可能
- [ ] ラベルが適切に設定されている
- [ ] README が適切に表示されている
- [ ] License ファイルが含まれている

## 🆘 トラブルシューティング

### よくある問題

1. **Push が拒否される**
   ```bash
   # SSH キーの確認
   ssh -T git@github.com
   
   # HTTPS の場合は Personal Access Token を確認
   gh auth status
   ```

2. **CI/CD が失敗する**
   - Actions タブでエラーログを確認
   - Secrets が正しく設定されているか確認
   - workflow ファイルの構文チェック

3. **Branch protection rules でマージできない**
   - 必要なステータスチェックが通っているか確認
   - レビューが完了しているか確認

## 🎯 次のステップ

リポジトリ設定完了後:
1. [CONTRIBUTING.md](CONTRIBUTING.md) を読んで開発ワークフローを理解
2. [INSTALL.md](INSTALL.md) に従って開発環境をセットアップ
3. 初回の Issue または Pull Request を作成してワークフローをテスト

---

**リポジトリURL**: `https://github.com/YOUR_USERNAME/g-kentei`

リポジトリが正常に設定されました！🎉