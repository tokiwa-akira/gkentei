## 1. 背景と目的
- **背景**  
  - G検定の受験者数は年々増加し、参考書・動画は多いが「完全オフライン × 自動テスト生成 × 学習分析」を満たす無料ツールは存在しない。  
- **目的**  
  1. 個人学習者が **広告・通信なし** で大量演習・模試を行える環境を提供  
  2. スクレイピング＋Local LLM により **運営者依存せず自動で問題を増殖**  
  3. 学習ログをローカルに蓄積し、**自己分析** できるダッシュボードを実装  

---

## 2. 全体アーキテクチャ

```text
┌───────────────┐
│   React PWA   │  ←── Service Worker (完全オフライン)
└───────────────┘
          ▲ REST / WS
          ▼
┌───────────────────────────────┐
│          FastAPI Core          │─┬─┐
│  ├─ 採点API / テスト生成API     │ │ │
│  ├─ LLM API (paraphrase/explain)│ │ │
│  └─ 学習ログAPI                │ │ │
└───────────────────────────────┘ │ │
     ▲         ▲                  │ │
     │         │                  │ │
┌────┴───┐ ┌───┴─────────┐   ┌────┴─────────┐
│Chroma  │ │SQLite (FTS) │   │Scraper Worker│
│VectorDB│ │Problem table│   │Playwright    │
└────────┘ └─────────────┘   └──────────────┘
             ▲                      ▲
             │                      │
     local files (/data)   cron or CLI trigger


⸻

3. 機能要件

区分	機能	概要
F1	問題データ収集	Playwright + BeautifulSoup で Web 記事をクロールし、正規表現で問と選択肢を抽出
F2	パラフレーズ生成	Local LLM (Llama-3-ELYZA-JP-8B-Q4 等) で著作権に配慮した別表現を生成
F3	問題管理	タグ・難易度・出典を付与し SQLite & Chroma に保存（FTS + Embedding）
F4	学習モード	用語カード / 分野別演習（SM-2 熟練度更新）
F5	模試モード	分野比率・問数・時間を指定しランダム生成、タイマー・一時保存
F6	採点・解説	正誤判定＋スコア計算、LLM で解説ドラフト提示
F7	学習分析	日次ヒートマップ、正答率推移、分野別レーダーチャート
F8	設定・バックアップ	テーマ切替、JSON/CSV エクスポート、Git/GDrive バックアップ（任意機能）


⸻

4. 非機能要件
	•	オフライン動作：インストール後は通信不要（PWA + Service Worker）
	•	ライセンス：OSS (MIT) を基本、クローラ取得データは出典・利用目的を明示
	•	パフォーマンス：オフライン PC (16 GB RAM, CPU 8-core) で 1 問生成 ≤ 5 s
	•	セキュリティ：外部送信しない・個人情報なし
	•	拡張性：Docker-Compose 一発構築、モデル・DB 差替え可

⸻

5. 技術スタック

層	採用技術	採用理由	代替候補
フロント	React + Vite + TypeScript	PWA 化容易・エコシステム豊富	SvelteKit
UI	Mantine UI	軽量＋ダークモード	Chakra-UI
グラフ	Chart.js (react-chartjs-2)	学習分析に十分、サイズ小	ECharts
バックエンド	FastAPI + uvicorn	型安全・AutoDocs・非同期	Flask
DB	SQLite (FTS5)	単一ファイル・高速全文検索	DuckDB
Vector	Chroma	ローカル完結・LangChain 対応	Milvus lite
LLM	llama-cpp-python + Llama-3-ELYZA-JP-8B-Q4	GPUなしでも動く日本語モデル	Ollama
Scraper	Playwright + BeautifulSoup4	SPA 対応・堅牢	Selenium
DevOps	Docker-Compose, pre-commit	再現性と品質担保	Nix


⸻

6. データモデル（抜粋）

erDiagram
  Problem ||--o{ Choice : has
  Problem {
    int id PK
    text question
    text answer
    text explanation
    int difficulty
    text tags
    text source_url
    datetime created_at
  }
  Choice {
    int id PK
    int problem_id FK
    char label
    text body
    bool is_correct
  }
  AnswerLog {
    int id PK
    int problem_id FK
    bool is_correct
    int time_ms
    datetime answered_at
  }


⸻

7. 開発ロードマップ

フェーズ	期間	マイルストーン
P0: 準備	0.5 週	リポジトリ初期化 / Docker-Compose 雛形 / pre-commit
P1: コア機能 MVP	1.5 週	DB スキーマ・Scraper・LLM パラフレーズ・API (テスト生成/採点) 完成
P2: UI MVP	1 週	React 画面 (演習・模試) + Service Worker + タイマー
P3: 学習分析	0.5 週	ダッシュボード (Chart.js) 実装
P4: βリリース	0.5 週	インストーラ・ドキュメント・ユーザーテスト
P5: 拡張	任意	OCR 連携 / Adaptive Learning / Docker Hub 公開


⸻

8. タスクリスト（Backlog）

ID	タスク	優先度	見積(h)	完了条件
T-01	DB スキーマ定義 & Alembic マイグレーション	A	4	CI で pytest 緑
T-02	Playwright 基盤＋robots.txt 準拠 DL	A	3	任意 URL 取得成功
T-03	問題抽出 RegExp & JSON 化	A	3	90% 正確率
T-04	llama-cpp Paraphrase API (/llm/paraphrase)	A	5	同意義・文章差分 > 70%
T-05	Chroma セットアップ＋検索エンドポイント	A	4	cosine sim で類似問検索
T-06	テスト生成ロジック (難易度/分野mix)	A	3	単体テスト通過
T-07	採点・結果 API + pandas 集計	B	4	スコア/項目別正答率
T-08	React 問題ビュー + タイマー	B	6	UX テスト OK
T-09	React 模試結果・解説画面	B	4	正誤・解説表示
T-10	学習ダッシュボード (Chart.js)	C	5	日次ヒートマップ
T-11	Docker-Compose + README	C	2	docker compose up 実行可
T-12	ユーザー設定 & バックアップ	C	3	JSON export/import


⸻

9. リスクと対策

リスク	影響	対策
スクレイピング禁止ページ増加	問題不足	著作権フリー記事 & 体験記を優先／ブックマークレット手動追加
Local LLM 精度不足	不自然なパラフレーズ	小規模 LoRA 追加学習、手動レビュー UI
モデルサイズによる動作遅延	UX 低下	4-bit 量子化、rinna-3.6B オプション
PWA キャッシュ破損	ロード不能	バージョニング＋キャッシュクリア API


⸻

10. OSS ライセンス方針
	•	本ツール: MIT ライセンス
	•	依存 OSS はそれぞれの LICENSE を同梱
	•	取得した問題文は 非商用・教育目的のみ再利用可 の CC-BY アノテーションを付与

⸻

11. 参考実装リンク
	•	llama-cpp-python: https://github.com/abetlen/llama-cpp-python
	•	Chroma: https://github.com/chroma-core/chroma
	•	Playwright: https://playwright.dev/python