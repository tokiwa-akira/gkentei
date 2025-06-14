#!/usr/bin/env python3
"""
G検定問題HTML解析エンジン
Usage: python parser.py <html_file>
"""

import re
import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup


class QuestionExtractor:
    """四択問題抽出クラス"""
    
    def __init__(self):
        # 問題パターン（複数形式に対応）
        self.question_patterns = [
            r'問\s*\d*[：:．.]?\s*(.+?)(?=①|A\.|1\.|（1）|\(1\))',
            r'Q\s*\d*[：:．.]?\s*(.+?)(?=①|A\.|1\.|（1）|\(1\))',
            r'設問\s*\d*[：:．.]?\s*(.+?)(?=①|A\.|1\.|（1）|\(1\))',
            r'【問題】\s*(.+?)(?=①|A\.|1\.|（1）|\(1\))',
        ]
        
        # 選択肢パターン（優先順位順）
        self.choice_patterns = [
            # ①②③④ 形式
            (r'([①②③④])\s*([^①②③④]+?)(?=②|③|④|正解|答え|解説|$)', ['①', '②', '③', '④']),
            # A. B. C. D. 形式
            (r'([A-D])\.\s*([^A-D\.]+?)(?=[A-D]\.|正解|答え|解説|$)', ['A', 'B', 'C', 'D']),
            # 1. 2. 3. 4. 形式
            (r'([1-4])\.\s*([^1-4\.]+?)(?=[1-4]\.|正解|答え|解説|$)', ['1', '2', '3', '4']),
            # （1）（2）（3）（4） 形式
            (r'（([1-4])）\s*([^（）]+?)(?=（[1-4]）|正解|答え|解説|$)', ['1', '2', '3', '4']),
            # (1) (2) (3) (4) 形式
            (r'\(([1-4])\)\s*([^()]+?)(?=\([1-4]\)|正解|答え|解説|$)', ['1', '2', '3', '4']),
        ]
        
        # 正解パターン
        self.answer_patterns = [
            r'(?:正解|答え)[：:．.\s]*([A-D①②③④１-４1-4])',
            r'(?:正答|解答)[：:．.\s]*([A-D①②③④１-４1-4])',
            r'Answer[：:．.\s]*([A-D①②③④１-４1-4])',
        ]
        
        # 全角数字→半角数字変換マップ
        self.zenkaku_map = str.maketrans('１２３４', '1234')

    def extract_text_from_html(self, html_content: str) -> str:
        """HTMLから本文テキストを抽出"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 不要なタグを除去
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # 本文候補を優先順位で取得
        main_content = None
        
        # 1. main, article, .content などのメインコンテンツ
        for selector in ['main', 'article', '.content', '.main', '#content', '#main']:
            element = soup.select_one(selector)
            if element:
                main_content = element.get_text()
                break
        
        # 2. 見つからない場合は body 全体
        if not main_content:
            body = soup.find('body')
            main_content = body.get_text() if body else soup.get_text()
        
        # テキスト正規化
        text = re.sub(r'\s+', ' ', main_content).strip()
        return text

    def find_question(self, text: str) -> Optional[str]:
        """問題文を抽出"""
        for pattern in self.question_patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                question = match.group(1).strip()
                # 最低文字数チェック（短すぎる場合は除外）
                if len(question) > 10:
                    return self._clean_text(question)
        return None

    def find_choices(self, text: str) -> Tuple[List[Dict], str]:
        """選択肢を抽出（選択肢リストと使用された形式を返す）"""
        for pattern, labels in self.choice_patterns:
            matches = list(re.finditer(pattern, text, re.DOTALL))
            
            if len(matches) >= 3:  # 最低3つの選択肢が必要
                choices = []
                for match in matches[:4]:  # 最大4つ
                    label = match.group(1)
                    body = self._clean_text(match.group(2))
                    
                    # 空の選択肢をスキップ
                    if len(body) > 2:
                        choices.append({
                            "label": label,
                            "body": body,
                            "is_correct": False
                        })
                
                if len(choices) >= 3:
                    return choices, labels[0]  # 成功した形式を返す
        
        return [], ""

    def find_answer(self, text: str, choice_format: str) -> Optional[str]:
        """正解を抽出"""
        for pattern in self.answer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                answer = match.group(1).translate(self.zenkaku_map)
                return self._normalize_answer_label(answer, choice_format)
        return None

    def _normalize_answer_label(self, answer: str, choice_format: str) -> str:
        """正解ラベルを選択肢形式に合わせて正規化"""
        answer = answer.translate(self.zenkaku_map)
        
        # ①②③④ → A,B,C,D への変換
        if choice_format == '①':
            mapping = {'①': 'A', '②': 'B', '③': 'C', '④': 'D'}
            return mapping.get(answer, answer)
        # 数字 → A,B,C,D への変換
        elif choice_format in ['1', '（1）', '(1)']:
            mapping = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
            return mapping.get(answer, answer)
        
        return answer.upper()

    def _clean_text(self, text: str) -> str:
        """テキストのクリーニング"""
        # 余分な空白・改行を削除
        text = re.sub(r'\s+', ' ', text).strip()
        # 特殊文字のクリーニング
        text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3400-\u4DBF、。！？（）()．.,!?]', '', text)
        return text

    def extract_question(self, html_content: str) -> Optional[Dict]:
        """HTMLから四択問題を抽出"""
        try:
            # HTMLからテキスト抽出
            text = self.extract_text_from_html(html_content)
            
            # 問題文抽出
            question = self.find_question(text)
            if not question:
                return None
            
            # 選択肢抽出
            choices, choice_format = self.find_choices(text)
            if len(choices) < 3:
                return None
            
            # 正解抽出
            correct_answer = self.find_answer(text, choice_format)
            
            # 正解をマーク
            if correct_answer:
                for choice in choices:
                    if choice["label"].upper() == correct_answer.upper():
                        choice["is_correct"] = True
                        break
            
            # A, B, C, D 形式に統一
            normalized_choices = []
            labels = ['A', 'B', 'C', 'D']
            for i, choice in enumerate(choices[:4]):
                normalized_choices.append({
                    "label": labels[i],
                    "body": choice["body"],
                    "is_correct": choice["is_correct"]
                })
            
            return {
                "question": question,
                "choices": normalized_choices
            }
            
        except Exception as e:
            print(f"Error extracting question: {e}", file=sys.stderr)
            return None


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='G検定問題HTML解析エンジン')
    parser.add_argument('html_file', help='解析するHTMLファイル')
    parser.add_argument('--debug', action='store_true', help='デバッグモード')
    
    args = parser.parse_args()
    
    # HTMLファイル読み込み
    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"Error: File {html_path} not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        # UTF-8で読めない場合はShift_JISを試す
        try:
            with open(html_path, 'r', encoding='shift_jis') as f:
                html_content = f.read()
        except UnicodeDecodeError:
            print("Error: Unable to decode HTML file", file=sys.stderr)
            sys.exit(1)
    
    # 問題抽出
    extractor = QuestionExtractor()
    result = extractor.extract_question(html_content)
    
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.debug:
            print("No question found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()