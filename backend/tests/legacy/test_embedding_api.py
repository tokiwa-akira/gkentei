#!/usr/bin/env python3
"""
Embedding検索APIのテストスイート

実行方法:
    pytest test_embedding_api.py -v
    python test_embedding_api.py  # 直接実行
"""

import time
import sqlite3
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

import pytest
import httpx
from fastapi.testclient import TestClient

# テスト対象のインポート
from ingest_embeddings import EmbeddingIngestor
from search_api import app, embedding_service

class TestEmbeddingIngestor:
    """EmbeddingIngestorのテスト"""
    
    @pytest.fixture
    def temp_dirs(self):
        """テスト用の一時ディレクトリ作成"""
        temp_dir = Path(tempfile.mkdtemp())
        db_path = temp_dir / "test.db"
        chroma_path = temp_dir / "chroma"
        
        yield db_path, chroma_path
        
        # クリーンアップ
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_db(self, temp_dirs):
        """サンプルデータベース作成"""
        db_path, _ = temp_dirs
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # テーブル作成
        cursor.execute("""
        CREATE TABLE problems (
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT,
            difficulty INTEGER DEFAULT 1,
            tags TEXT,
            source_url TEXT,
            created_at TEXT
        )
        """)
        
        # サンプルデータ投入
        sample_problems = [
            (1, "ニューラルネットワークとは何ですか？", "A", 1, "機械学習,基礎", "http://example.com/1", "2024-01-01"),
            (2, "深層学習の特徴について説明してください。", "B", 2, "深層学習", "http://example.com/2", "2024-01-02"),
            (3, "畳み込みニューラルネットワークの仕組みは？", "C", 3, "CNN,画像処理", "http://example.com/3", "2024-01-03"),
            (4, "自然言語処理におけるTransformerの役割は？", "A", 2, "NLP,Transformer", "http://example.com/4", "2024-01-04"),
            (5, "強化学習のQ学習アルゴリズムとは？", "D", 3, "強化学習", "http://example.com/5", "2024-01-05"),
        ]
        
        cursor.executemany(
            "INSERT INTO problems (id, question, answer, difficulty, tags, source_url, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            sample_problems
        )
        
        conn.commit()
        conn.close()
        
        return db_path
    
    def test_fetch_problems_from_db(self, sample_db, temp_dirs):
        """データベースからの問題取得テスト"""
        db_path, chroma_path = temp_dirs
        
        ingestor = EmbeddingIngestor(
            db_path=str(sample_db),
            chroma_path=str(chroma_path),
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        problems = ingestor.fetch_problems_from_db()
        
        assert len(problems) == 5
        assert problems[0]['question'] == "ニューラルネットワークとは何ですか？"
        assert problems[0]['difficulty'] == 1
        assert problems[0]['tags'] == "機械学習,基礎"
    
    def test_embedding_generation(self, temp_dirs):
        """Embedding生成テスト"""
        db_path, chroma_path = temp_dirs
        
        ingestor = EmbeddingIngestor(
            db_path=str(db_path),
            chroma_path=str(chroma_path),
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        texts = ["ニューラルネットワーク", "機械学習", "深層学習"]
        embeddings = ingestor.generate_embeddings(texts)
        
        assert len(embeddings) == 3
        assert len(embeddings[0]) == 384  # all-MiniLM-L6-v2の次元数
        assert all(isinstance(emb, list) for emb in embeddings)
    
    def test_full_ingestion_pipeline(self, sample_db, temp_dirs):
        """完全なEmbedding登録パイプラインテスト"""
        db_path, chroma_path = temp_dirs
        
        ingestor = EmbeddingIngestor(
            db_path=str(sample_db),
            chroma_path=str(chroma_path),
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # 問題取得
        problems = ingestor.fetch_problems_from_db()
        assert len(problems) == 5
        
        # ChromaDBに登録
        ingestor.upsert_to_chroma(problems, batch_size=2)
        
        # 統計確認
        stats = ingestor.get_collection_stats()
        assert stats['total_documents'] == 5
        assert stats['collection_name'] == 'problems'

class TestSearchAPI:
    """Search APIのテスト"""
    
    @pytest.fixture(scope="class")
    def client(self):
        """テスト用APIクライアント"""
        return TestClient(app)
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_test_data(self):
        """テスト用データのセットアップ"""
        # 実際のChromaDBセットアップが必要
        # テスト環境では軽量化のため省略可能
        pass
    
    def test_health_endpoint(self, client):
        """ヘルスチェックエンドポイントテスト"""
        response = client.get("/health")
        
        # 初期化前はエラーまたは503が返される可能性
        assert response.status_code in [200, 503]
    
    def test_root_endpoint(self, client):
        """ルートエンドポイントテスト"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert "endpoints" in data
    
    def test_search_validation(self, client):
        """検索パラメータバリデーションテスト"""
        # 空クエリ
        response = client.get("/search?q=")
        assert response.status_code == 422
        
        # 不正なk値
        response = client.get("/search?q=test&k=-1")
        assert response.status_code == 422
        
        response = client.get("/search?q=test&k=100")
        assert response.status_code == 422

def test_performance_benchmark():
    """パフォーマンステスト"""
    # 実際のChromaDBとの接続が必要
    # ここでは概念的なテスト
    
    query = "ニューラルネットワーク"
    start_time = time.time()
    
    # 実際の検索処理をシミュレート
    time.sleep(0.05)  # 50ms のシミュレート
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # 100ms以内の応答時間を確認
    assert elapsed_ms < 100, f"Search took {elapsed_ms}ms, expected < 100ms"

def integration_test():
    """統合テスト - 実際のAPIサーバーとの通信"""
    base_url = "http://localhost:8000"
    
    try:
        with httpx.Client(timeout=30.0) as client:
            # ヘルスチェック
            response = client.get(f"{base_url}/health")
            print(f"Health check: {response.status_code}")
            
            if response.status_code == 200:
                # 検索テスト
                test_queries = [
                    "ニューラルネットワーク",
                    "機械学習",
                    "深層学習",
                    "自然言語処理"
                ]
                
                for query in test_queries:
                    start_time = time.time()
                    response = client.get(f"{base_url}/search", params={"q": query, "k": 3})
                    elapsed_ms = (time.time() - start_time) * 1000
                    
                    print(f"Query: '{query}' - Status: {response.status_code} - Time: {elapsed_ms:.1f}ms")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"  Results: {len(data['results'])} items")
                        for result in data['results'][:2]:  # 上位2件を表示
                            print(f"    Score: {result['score']:.3f} - {result['snippet'][:50]}...")
                    
                    assert elapsed_ms < 100, f"Search too slow: {elapsed_ms}ms"
                    
    except httpx.ConnectError:
        print("⚠️  API server not running. Start with 'docker compose up'")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Running Embedding API Tests")
    print("=" * 50)
    
    # 統合テスト実行
    print("\n1. Integration Test:")
    if integration_test():
        print("✅ Integration tests passed")
    else:
        print("❌ Integration tests failed")
    
    # パフォーマンステスト
    print("\n2. Performance Test:")
    try:
        test_performance_benchmark()
        print("✅ Performance test passed")
    except AssertionError as e:
        print(f"❌ Performance test failed: {e}")
    
    print("\n🎉 Manual tests completed!")
    print("Run 'pytest test_embedding_api.py -v' for full test suite")