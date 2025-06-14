#!/usr/bin/env python3
"""
parser.py のデモスクリプト
"""

import tempfile
import os
import subprocess
import sys
from pathlib import Path

def create_demo_html_files():
    """デモ用のHTMLファイルを作成"""
    demo_files = []
    
    # パターン1: 問+①②③④
    html1 = """
    <!DOCTYPE html>
    <html><head><title>G検定 問題1</title></head>
    <body>
        <main>
            <h2>問1: 機械学習の三大要素として正しいものはどれか。</h2>
            <p>①データ、アルゴリズム、計算能力</p>
            <p>②データ、プログラム、ハードウェア</p>
            <p>③モデル、学習、推論</p>
            <p>④入力、処理、出力</p>
            <p>正解：①</p>
        </main>
    </body></html>
    """
    
    # パターン2: Q+A.B.C.D.
    html2 = """
    <!DOCTYPE html>
    <html><head><title>G検定 問題2</title></head>
    <body>
        <article>
            <h3>Q2. ディープラーニングで使用されるオプティマイザーとして最も基本的なものは？</h3>
            <p>A. Adam</p>
            <p>B. 確率的勾配降下法（SGD）</p>
            <p>C. RMSprop</p>
            <p>D. AdaGrad</p>
            <footer>答え: B</footer>
        </article>
    </body></html>
    """
    
    # パターン3: 設問+1.2.3.4.
    html3 = """
    <!DOCTYPE html>
    <html><head><title>G検定 問題3</title></head>
    <body>
        <div class="content">
            <p>設問3：CNNにおけるプーリング層の役割として正しいものは？</p>
            <ul>
                <li>1. 特徴マップのサイズを削減する</li>
                <li>2. 重みパラメータを増やす</li>
                <li>3. 活性化関数を適用する</li>
                <li>4. バッチ正規化を行う</li>
            </ul>
            <p class="answer">正解：1</p>
        </div>
    </body></html>
    """
    
    # パターン4: 【問題】+（1）（2）（3）（4）
    html4 = """
    <!DOCTYPE html>
    <html><head><title>G検定 問題4</title></head>
    <body>
        <main>
            <h2>【問題】自然言語処理におけるAttentionメカニズムの特徴は？</h2>
            <p>（1）固定長ベクトルに圧縮する</p>
            <p>（2）入力の重要な部分に注目する</p>
            <p>（3）順序情報を無視する</p>
            <p>（4）文字レベルで処理する</p>
            <p>正答：（2）</p>
        </main>
    </body></html>
    """
    
    # パターン5: 問+(1)(2)(3)(4)
    html5 = """
    <!DOCTYPE html>
    <html><head><title>G検定 問題5</title></head>
    <body>
        <section>
            <p>問5. 強化学習における価値関数の説明として適切なものは？</p>
            <p>(1) 行動の即座の報酬を表す</p>
            <p>(2) 状態または状態-行動ペアの価値を評価する</p>
            <p>(3) エピソードの終了条件を決める</p>
            <p>(4) エージェントの行動を直接決定する</p>
            <div>正解：２</div>
        </section>
    </body></html>
    """
    
    # 一時ファイルとして作成
    for i, html_content in enumerate([html1, html2, html3, html4, html5], 1):
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'_demo{i}.html', 
                                       delete=False, encoding='utf-8') as f:
            f.write(html_content)
            demo_files.append(f.name)
    
    return demo_files

def run_parser_demo():
    """parser.pyのデモを実行"""
    print("🚀 G検定問題抽出エンジン デモ実行\n")
    
    # デモファイル作成
    demo_files = create_demo_html_files()
    
    try:
        for i, file_path in enumerate(demo_files, 1):
            print(f"📄 問題 {i}: {Path(file_path).name}")
            print("-" * 50)
            
            # parser.py実行
            result = subprocess.run([
                sys.executable, 'parser.py', file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"❌ エラー: {result.stderr}")
            
            print()
    
    finally:
        # 一時ファイル削除
        for file_path in demo_files:
            try:
                os.unlink(file_path)
            except:
                pass

def run_tests():
    """テスト実行"""
    print("🧪 テスト実行中...\n")
    
    # pytest実行
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 'tests/test_parser.py', '-v'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='G検定問題抽出エンジン デモ')
    parser.add_argument('--test', action='store_true', help='テストを実行')
    parser.add_argument('--demo', action='store_true', help='デモを実行')
    
    args = parser.parse_args()
    
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.demo:
        run_parser_demo()
    else:
        print("使用方法:")
        print("  python demo.py --demo   # デモ実行")
        print("  python demo.py --test   # テスト実行")