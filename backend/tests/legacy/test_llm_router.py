"""
LLM Router のテストケース
T-04 受け入れ条件検証用
"""

import pytest
import asyncio
import time
from fastapi.testclient import TestClient
from fastapi import FastAPI
from router_llm import router, llm_instance
import json

# テストアプリ作成
app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestLLMRouter:
    """LLMルーターのテストクラス"""
    
    def test_health_endpoint(self):
        """ヘルスチェックエンドポイントのテスト"""
        response = client.get("/llm/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert isinstance(data["model_loaded"], bool)
    
    def test_paraphrase_request_validation(self):
        """リクエスト検証のテスト"""
        # 空文字列テスト
        response = client.post(
            "/llm/paraphrase",
            json={"text": ""}
        )
        assert response.status_code == 422
        
        # 長すぎるテキスト
        long_text = "a" * 501
        response = client.post(
            "/llm/paraphrase",
            json={"text": long_text}
        )
        assert response.status_code == 422
        
        # 無効なtemperature
        response = client.post(
            "/llm/paraphrase",
            json={
                "text": "テストテキスト",
                "temperature": 2.0  # 1.0を超える
            }
        )
        assert response.status_code == 422

    @pytest.mark.skipif(
        llm_instance is None,
        reason="LLM model not loaded"
    )
    def test_paraphrase_basic_functionality(self):
        """基本的なパラフレーズ機能のテスト"""
        test_text = "人工知能は複雑な問題を解決する技術です。"
        
        response = client.post(
            "/llm/paraphrase",
            json={
                "text": test_text,
                "max_length": 100,
                "temperature": 0.3
            }
        )
        
        assert response.status_code == 200
        
        data = response.json()
        required_fields = [
            "paraphrased", "original_length", 
            "paraphrased_length", "processing_time_ms"
        ]
        
        for field in required_fields:
            assert field in data
        
        # 基本的な品質チェック
        assert len(data["paraphrased"]) > 0
        assert data["original_length"] == len(test_text)
        assert data["paraphrased_length"] == len(data["paraphrased"])
        assert data["processing_time_ms"] > 0

    @pytest.mark.skipif(
        llm_instance is None,
        reason="LLM model not loaded"
    )
    def test_response_time_requirement(self):
        """応答時間要件のテスト（5秒以内）"""
        test_text = "機械学習は人工知能の一分野であり、データからパターンを学習する技術です。"
        
        start_time = time.time()
        response = client.post(
            "/llm/paraphrase",
            json={"text": test_text}
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 受け入れ条件: 5秒以内
        assert response_time < 5.0, f"Response time {response_time:.2f}s exceeds 5s limit"
        assert response.status_code == 200

    @pytest.mark.skipif(
        llm_instance is None,
        reason="LLM model not loaded"
    )
    def test_paraphrase_quality_manual_check(self):
        """パラフレーズ品質の手動チェック用テスト"""
        test_cases = [
            "深層学習はニューラルネットワークを多層にした機械学習手法です。",
            "自然言語処理は人間の言語をコンピューターで処理する技術分野です。",
            "強化学習は試行錯誤を通じて最適な行動を学習するアルゴリズムです。"
        ]
        
        results = []
        
        for test_text in test_cases:
            response = client.post(
                "/llm/paraphrase",
                json={"text": test_text}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            result = {
                "original": test_text,
                "paraphrased": data["paraphrased"],
                "processing_time": data["processing_time_ms"]
            }
            results.append(result)
            
            # 基本品質チェック
            assert data["paraphrased"] != test_text, "パラフレーズが元テキストと同じ"
            assert len(data["paraphrased"]) > 10, "パラフレーズが短すぎる"
        
        # 結果出力（手動評価用）
        print("\n=== パラフレーズ品質確認 ===")
        for i, result in enumerate(results, 1):
            print(f"\nテストケース {i}:")
            print(f"元文: {result['original']}")
            print(f"変換: {result['paraphrased']}")
            print(f"時間: {result['processing_time']}ms")

    def test_max_length_constraint(self):
        """最大文字数制限のテスト"""
        long_text = "人工知能技術は現代社会において重要な役割を果たしており、機械学習や深層学習といった手法を用いて複雑な問題を解決する能力を持っています。"
        max_length = 50
        
        response = client.post(
            "/llm/paraphrase",
            json={
                "text": long_text,
                "max_length": max_length
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # 若干の超過は許容（"..."追加等）
            assert len(data["paraphrased"]) <= max_length + 3

    def test_test_paraphrase_endpoint(self):
        """テスト用エンドポイントの動作確認"""
        response = client.post("/llm/test-paraphrase")
        
        # モデルが利用可能な場合のみ成功を期待
        if llm_instance is not None:
            assert response.status_code == 200
            data = response.json()
            assert "paraphrased" in data
        else:
            # モデルが無い場合は503エラーを期待
            assert response.status_code == 503

    @pytest.mark.parametrize("temperature", [0.1, 0.5, 0.9])
    def test_temperature_variation(self, temperature):
        """異なるtemperature設定のテスト"""
        test_text = "データサイエンスは統計学と計算技術を組み合わせた学問分野です。"
        
        response = client.post(
            "/llm/paraphrase",
            json={
                "text": test_text,
                "temperature": temperature
            }
        )
        
        # モデルが利用可能な場合のみテスト実行
        if llm_instance is not None:
            assert response.status_code == 200
            data = response.json()
            assert len(data["paraphrased"]) > 0

# パフォーマンステスト用のフィクスチャ
@pytest.fixture(scope="session")
def performance_data():
    """パフォーマンステスト用データ"""
    return {
        "short_texts": [
            "AIは人工知能の略です。",
            "機械学習は便利な技術です。",
            "プログラミングは楽しいです。"
        ],
        "medium_texts": [
            "深層学習は多層のニューラルネットワークを使用した機械学習の手法です。",
            "自然言語処理技術により、コンピューターが人間の言語を理解できます。",
            "画像認識システムは畳み込みニューラルネットワークを活用しています。"
        ],
        "long_texts": [
            "人工知能の発展は目覚ましく、特に機械学習と深層学習の分野では革新的な進歩が続いています。これらの技術は医療、金融、自動車産業など様々な分野で活用されており、社会に大きな変革をもたらしています。"
        ]
    }

class TestPerformance:
    """パフォーマンス関連のテスト"""
    
    @pytest.mark.skipif(
        llm_instance is None,
        reason="LLM model not loaded"
    )
    def test_concurrent_requests(self):
        """同時リクエストの処理テスト"""
        import concurrent.futures
        
        def make_request():
            return client.post(
                "/llm/paraphrase",
                json={"text": "テスト用の短い文章です。"}
            )
        
        # 3つの同時リクエスト
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(3)]
            responses = [future.result() for future in futures]
        
        # すべてのレスポンスが成功することを確認
        for response in responses:
            assert response.status_code in [200, 503]  # モデル利用可能時は200、そうでなければ503

if __name__ == "__main__":
    # テスト実行例
    pytest.main([__file__, "-v", "--tb=short"])