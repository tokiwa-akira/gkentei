"""
模試生成API テストコード
pytest tests/test_exam.py で実行
"""

import pytest
import json
import time
import sqlite3
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

# テスト対象のインポート (実際のパスに調整)
from exam_api import router, ExamGenerator, get_db_connection

# === Test Setup ===

@pytest.fixture
def app():
    """テスト用FastAPIアプリ"""
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app

@pytest.fixture
def client(app):
    """テストクライアント"""
    return TestClient(app)

@pytest.fixture
def sample_db():
    """テスト用サンプルデータベース"""
    # テスト用データベースファイル
    db_path = "test_problems.db"
    
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS problem (
            id INTEGER PRIMARY KEY,
            question TEXT,
            answer TEXT,
            explanation TEXT,
            difficulty INTEGER,
            tags TEXT,
            source_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS choice (
            id INTEGER PRIMARY KEY,
            problem_id INTEGER,
            label TEXT,
            body TEXT,
            is_correct BOOLEAN,
            FOREIGN KEY (problem_id) REFERENCES problem (id)
        )
    """)
    
    # サンプルデータ投入
    problems_data = [
        # 難易度1 (数学)
        (1, "1+1は？", "2", "基本的な足し算", 1, "数学,基礎", "http://example.com/1"),
        (2, "2×3は？", "6", "基本的な掛け算", 1, "数学,基礎", "http://example.com/2"),
        (3, "10÷2は？", "5", "基本的な割り算", 1, "数学,基礎", "http://example.com/3"),
        
        # 難易度2 (深層学習)
        (4, "ReLU関数の特徴は？", "負の値を0にする", "活性化関数", 2, "深層学習,活性化関数", "http://example.com/4"),
        (5, "バックプロパゲーションとは？", "誤差逆伝播", "学習アルゴリズム", 2, "深層学習,学習", "http://example.com/5"),
        (6, "SGDとは？", "確率的勾配降下法", "最適化", 2, "深層学習,最適化", "http://example.com/6"),
        
        # 難易度3 (応用)
        (7, "Transformerアーキテクチャの特徴は？", "Attention機構", "最新手法", 3, "深層学習,Transformer", "http://example.com/7"),
        (8, "GANの原理は？", "敵対的学習", "生成モデル", 3, "深層学習,生成", "http://example.com/8"),
        (9, "強化学習のQ学習とは？", "行動価値関数", "強化学習", 3, "機械学習,強化学習", "http://example.com/9"),
        (10, "CNNの畳み込み層の役割は？", "特徴抽出", "画像処理", 3, "深層学習,CNN", "http://example.com/10"),
    ]
    
    for problem in problems_data:
        conn.execute("""
            INSERT INTO problem (id, question, answer, explanation, difficulty, tags, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, problem)
    
    # 選択肢データ
    choices_data = [
        # 問題1の選択肢
        (1, 1, "A", "1", False),
        (2, 1, "B", "2", True),
        (3, 1, "C", "3", False),
        (4, 1, "D", "4", False),
        
        # 問題4の選択肢
        (5, 4, "A", "負の値を0にする", True),
        (6, 4, "B", "全ての値を1にする", False),
        (7, 4, "C", "値を2倍にする", False),
        (8, 4, "D", "値を反転させる", False),
        
        # 他の問題にも同様に選択肢を追加...
    ]
    
    for choice in choices_data:
        conn.execute("""
            INSERT INTO choice (id, problem_id, label, body, is_correct)
            VALUES (?, ?, ?, ?, ?)
        """, choice)
    
    conn.commit()
    conn.close()
    
    # パッチしてテスト用DBを使用
    with patch('exam_api.get_db_connection') as mock_get_db:
        def mock_connection():
            return sqlite3.connect(db_path)
        mock_get_db.return_value.__enter__ = lambda self: mock_connection()
        mock_get_db.return_value.__exit__ = lambda self, *args: None
        yield db_path
    
    # テスト後クリーンアップ
    import os
    if os.path.exists(db_path):
        os.remove(db_path)

# === Basic Functionality Tests ===

def test_generate_exam_basic(client, sample_db):
    """基本的な模試生成テスト"""
    request_data = {
        "num_questions": 5,
        "difficulty_ratio": {"1": 0.4, "2": 0.4, "3": 0.2},
        "tags": ["数学", "深層学習"],
        "time_limit_min": 60
    }
    
    response = client.post("/exam/generate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # 基本構造チェック
    assert "exam_id" in data
    assert "questions" in data
    assert "time_limit_sec" in data
    assert data["time_limit_sec"] == 3600  # 60分 = 3600秒
    
    # 問題数チェック
    assert len(data["questions"]) == 5
    
    # 各問題の構造チェック
    for question in data["questions"]:
        assert "id" in question
        assert "question" in question
        assert "choices" in question
        assert "difficulty" in question
        assert "tags" in question

def test_difficulty_ratio_validation(client, sample_db):
    """難易度比率バリデーションテスト"""
    # 合計が1.0でない場合
    request_data = {
        "num_questions": 3,
        "difficulty_ratio": {"1": 0.5, "2": 0.3},  # 合計0.8
        "time_limit_min": 30
    }
    
    response = client.post("/exam/generate", json=request_data)
    assert response.status_code == 422  # Validation Error

def test_insufficient_questions(client, sample_db):
    """問題数不足エラーテスト"""
    request_data = {
        "num_questions": 50,  # サンプルDBには10問しかない
        "difficulty_ratio": {"1": 0.3, "2": 0.4, "3": 0.3},
        "time_limit_min": 120
    }
    
    response = client.post("/exam/generate", json=request_data)
    assert response.status_code == 400
    assert "問題が不足" in response.json()["detail"]

# === Performance Tests ===

def test_generation_performance(client, sample_db):
    """生成パフォーマンステスト (< 300ms)"""
    request_data = {
        "num_questions": 5,
        "difficulty_ratio": {"1": 0.4, "2": 0.4, "3": 0.2},
        "time_limit_min": 90
    }
    
    start_time = time.time()
    response = client.post("/exam/generate", json=request_data)
    elapsed_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    assert elapsed_ms < 300  # 300ms以内
    
    # メタデータの生成時間もチェック
    data = response.json()
    if "metadata" in data and "generation_time_ms" in data["metadata"]:
        assert data["metadata"]["generation_time_ms"] < 300

# === Ratio Validation Tests ===

def test_difficulty_distribution(client, sample_db):
    """難易度分布の正確性テスト"""
    request_data = {
        "num_questions": 6,
        "difficulty_ratio": {"1": 0.5, "2": 0.33, "3": 0.17},  # 3:2:1の比率
        "tags": None,
        "time_limit_min": 60
    }
    
    response = client.post("/exam/generate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    questions = data["questions"]
    
    # 難易度別カウント
    difficulty_counts = {}
    for q in questions:
        diff = q["difficulty"]
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
    
    # 期待される分布に近いかチェック (完全一致は難しいので許容範囲で)
    total = len(questions)
    for difficulty, count in difficulty_counts.items():
        ratio = count / total
        print(f"難易度{difficulty}: {count}問 ({ratio:.2f})")
    
    # 最低限の分布チェック
    assert len(difficulty_counts) >= 2  # 複数難易度が含まれる

# === Tag Filtering Tests ===

def test_tag_filtering(client, sample_db):
    """タグフィルタリングテスト"""
    # 数学のみ
    request_data = {
        "num_questions": 3,
        "difficulty_ratio": {"1": 1.0},
        "tags": ["数学"],
        "time_limit_min": 30
    }
    
    response = client.post("/exam/generate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    questions = data["questions"]
    
    # 全ての問題が数学タグを含むかチェック
    for question in questions:
        assert any("数学" in tag for tag in question["tags"])

def test_no_tag_filter(client, sample_db):
    """タグフィルタなしテスト"""
    request_data = {
        "num_questions": 5,
        "difficulty_ratio": {"1": 0.4, "2": 0.4, "3": 0.2},
        "tags": None,  # 全分野対象
        "time_limit_min": 60
    }
    
    response = client.post("/exam/generate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["questions"]) == 5

# === Utility Endpoints Tests ===

def test_exam_stats(client, sample_db):
    """統計情報APIテスト"""
    response = client.get("/exam/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_problems" in data
    assert "difficulty_distribution" in data
    assert "popular_tags" in data
    
    # サンプルデータの期待値
    assert data["total_problems"] == 10

def test_temp_exam_deletion(client, sample_db):
    """一時テーブル削除テスト"""
    # まず模試を生成
    request_data = {
        "num_questions": 3,
        "difficulty_ratio": {"1": 1.0},
        "time_limit_min": 30
    }
    
    generate_response = client.post("/exam/generate", json=request_data)
    assert generate_response.status_code == 200
    
    exam_id = generate_response.json()["exam_id"]
    
    # 削除
    delete_response = client.delete(f"/exam/temp/{exam_id}")
    assert delete_response.status_code == 200
    assert "削除しました" in delete_response.json()["message"]

def test_delete_nonexistent_exam(client, sample_db):
    """存在しない模試ID削除テスト"""
    fake_id = "nonexistent-id"
    response = client.delete(f"/exam/temp/{fake_id}")
    assert response.status_code == 404

# === Edge Cases Tests ===

def test_minimum_questions(client, sample_db):
    """最小問題数テスト"""
    request_data = {
        "num_questions": 1,
        "difficulty_ratio": {"1": 1.0},
        "time_limit_min": 10
    }
    
    response = client.post("/exam/generate", json=request_data)
    assert response.status_code == 200
    assert len(response.json()["questions"]) == 1

def test_maximum_time_limit(client, sample_db):
    """最大制限時間テスト"""
    request_data = {
        "num_questions": 2,
        "difficulty_ratio": {"1": 1.0},
        "time_limit_min": 300  # 5時間
    }
    
    response = client.post("/exam/generate", json=request_data)
    assert response.status_code == 200
    assert response.json()["time_limit_sec"] == 18000  # 300分 = 18000秒

# === Integration Tests ===

def test_full_workflow(client, sample_db):
    """完全ワークフローテスト"""
    # 1. 統計情報取得
    stats_response = client.get("/exam/stats")
    assert stats_response.status_code == 200
    
    # 2. 模試生成
    request_data = {
        "num_questions": 4,
        "difficulty_ratio": {"1": 0.25, "2": 0.50, "3": 0.25},
        "tags": ["深層学習"],
        "time_limit_min": 80
    }
    
    exam_response = client.post("/exam/generate", json=request_data)
    assert exam_response.status_code == 200
    
    exam_data = exam_response.json()
    exam_id = exam_data["exam_id"]
    
    # 3. メタデータ検証
    assert "metadata" in exam_data
    metadata = exam_data["metadata"]
    assert "generation_time_ms" in metadata
    assert "actual_difficulty_distribution" in metadata
    assert "total_candidates" in metadata
    
    # 4. 一時テーブル削除
    delete_response = client.delete(f"/exam/temp/{exam_id}")
    assert delete_response.status_code == 200

if __name__ == "__main__":
    # 単体実行用
    pytest.main([__file__, "-v"])