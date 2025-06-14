#!/usr/bin/env python3
"""
G検定問題抽出エンジンのテスト
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys
import os

# パーサーモジュールをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from parser import QuestionExtractor


class TestQuestionExtractor:
    """問題抽出テストクラス"""
    
    @pytest.fixture
    def extractor(self):
        return QuestionExtractor()
    
    def create_test_html(self, content: str) -> str:
        """テスト用HTMLファイルを作成"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head><title>G検定練習問題</title></head>
        <body>
            <main>
                {content}
            </main>
        </body>
        </html>
        """
        return html_template
    
    def test_extract_basic_pattern1(self, extractor):
        """基本パターン1: 問+①②③④形式"""
        html_content = self.create_test_html("""
            <div>
                <p>問1: 機械学習において、教師あり学習の代表的なアルゴリズムはどれか。</p>
                <p>①線形回帰</p>
                <p>②k-means</p>
                <p>③主成分分析</p>
                <p>④階層クラスタリング</p>
                <p>正解：①</p>
            </div>
        """)
        
        result = extractor.extract_question(html_content)
        
        assert result is not None
        assert "機械学習において" in result["question"]
        assert len(result["choices"]) == 4
        assert result["choices"][0]["label"] == "A"
        assert result["choices"][0]["is_correct"] == True
        assert "線形回帰" in result["choices"][0]["body"]
    
    def test_extract_basic_pattern2(self, extractor):
        """基本パターン2: Q+A.B.C.D.形式"""
        html_content = self.create_test_html("""
            <div>
                <h3>Q2. ディープラーニングで使用される活性化関数として最も一般的なものは？</h3>
                <p>A. Sigmoid関数</p>
                <p>B. ReLU関数</p>
                <p>C. Tanh関数</p>
                <p>D. ステップ関数</p>
                <p>答え: B</p>
            </div>
        """)
        
        result = extractor.extract_question(html_content)
        
        assert result is not None
        assert "ディープラーニング" in result["question"]
        assert len(result["choices"]) == 4
        assert result["choices"][1]["label"] == "B"
        assert result["choices"][1]["is_correct"] == True
        assert "ReLU関数" in result["choices"][1]["body"]
    
    def test_extract_pattern3(self, extractor):
        """パターン3: 設問+1.2.3.4.形式"""
        html_content = self.create_test_html("""
            <div>
                <p>設問3：畳み込みニューラルネットワーク（CNN）の特徴として正しいものは次のうちどれか。</p>
                <div>
                    <p>1. 位置不変性を持つ</p>
                    <p>2. 回帰問題専用である</p>
                    <p>3. パラメータ数が全結合層より多い</p>
                    <p>4. 時系列データに最適化されている</p>
                </div>
                <p>正解：1</p>
            </div>
        """)
        
        result = extractor.extract_question(html_content)
        
        assert result is not None
        assert "畳み込みニューラルネットワーク" in result["question"]
        assert len(result["choices"]) == 4
        assert result["choices"][0]["is_correct"] == True
        assert "位置不変性" in result["choices"][0]["body"]
    
    def test_extract_pattern4(self, extractor):
        """パターン4: 【問題】+（1）（2）（3）（4）形式"""
        html_content = self.create_test_html("""
            <section>
                <h2>【問題】強化学習における報酬について正しい記述はどれか。</h2>
                <ul>
                    <li>（1）報酬は必ず正の値でなければならない</li>
                    <li>（2）報酬は環境から与えられるフィードバック信号である</li>
                    <li>（3）報酬は学習開始時に事前に設定する必要がある</li>
                    <li>（4）報酬は行動の直後に必ず与えられる</li>
                </ul>
                <p>正答：（2）</p>
            </section>
        """)
        
        result = extractor.extract_question(html_content)
        
        assert result is not None
        assert "強化学習" in result["question"]
        assert len(result["choices"]) == 4
        assert result["choices"][1]["is_correct"] == True
        assert "フィードバック信号" in result["choices"][1]["body"]
    
    def test_extract_pattern5(self, extractor):
        """パターン5: 問+(1)(2)(3)(4)形式+全角正解"""
        html_content = self.create_test_html("""
            <article>
                <p>問5. 自然言語処理において、Word2Vecの特徴として適切でないものはどれか。</p>
                <p>(1) 単語をベクトル表現に変換する</p>
                <p>(2) 意味的に似た単語は近いベクトル空間に配置される</p>
                <p>(3) 文法的な構造を直接学習する</p>
                <p>(4) Skip-gramとCBOWの2つのモデルがある</p>
                <div class="answer">
                    <p>解答：３</p>
                </div>
            </article>
        """)
        
        result = extractor.extract_question(html_content)
        
        assert result is not None
        assert "Word2Vec" in result["question"]
        assert len(result["choices"]) == 4
        assert result["choices"][2]["is_correct"] == True
        assert "文法的な構造" in result["choices"][2]["body"]
    
    def test_no_question_found(self, extractor):
        """問題が見つからない場合"""
        html_content = self.create_test_html("""
            <div>
                <p>これは普通の記事です。</p>
                <p>機械学習について説明します。</p>
                <p>特に選択肢はありません。</p>
            </div>
        """)
        
        result = extractor.extract_question(html_content)
        assert result is None
    
    def test_insufficient_choices(self, extractor):
        """選択肢が不十分な場合"""
        html_content = self.create_test_html("""
            <div>
                <p>問: 機械学習とは何か？</p>
                <p>①人工知能の一分野</p>
                <p>②コンピュータプログラム</p>
                <p>正解：①</p>
            </div>
        """)
        
        result = extractor.extract_question(html_content)
        assert result is None  # 選択肢が2つしかないため
    
    def test_text_cleaning(self, extractor):
        """テキストクリーニングのテスト"""
        # 余分な空白や改行が含まれたHTML
        html_content = self.create_test_html("""
            <div>
                <p>問1:    ディープラーニングにおいて、
                
                過学習を防ぐ手法として   適切なものはどれか。</p>
                <p>①   ドロップアウト   </p>
                <p>②データ拡張  　</p>
                <p>③　正則化　</p>
                <p>④   早期停止 </p>
                <p>正解：①</p>
            </div>
        """)
        
        result = extractor.extract_question(html_content)
        
        assert result is not None
        # 余分な空白が除去されていることを確認
        assert "  " not in result["question"]
        assert all("  " not in choice["body"] for choice in result["choices"])


def test_integration_with_file():
    """ファイル入出力の統合テスト"""
    # テスト用HTMLファイルを一時作成
    test_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
        <main>
            <h2>問1: ニューラルネットワークの基本構成要素は？</h2>
            <p>A. ニューロン</p>
            <p>B. アルゴリズム</p>
            <p>C. データベース</p>
            <p>D. インターフェース</p>
            <p>正解: A</p>
        </main>
    </body>
    </html>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(test_html)
        temp_path = f.name
    
    try:
        extractor = QuestionExtractor()
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = extractor.extract_question(content)
        
        assert result is not None
        assert "ニューラルネットワーク" in result["question"]
        assert len(result["choices"]) == 4
        assert result["choices"][0]["is_correct"] == True
        
        # JSON出力テスト
        json_output = json.dumps(result, ensure_ascii=False, indent=2)
        assert "ニューロン" in json_output
        
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])