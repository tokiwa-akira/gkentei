"""
模試生成API実装
/exam/generate エンドポイント
"""

import uuid
import random
import time
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
import sqlite3
from contextlib import contextmanager

# === Models ===

class DifficultyRatio(BaseModel):
    """難易度比率 (合計1.0になるよう検証)"""
    ratios: Dict[str, float] = Field(..., description="難易度レベル:比率のマップ")
    
    @validator('ratios')
    def validate_ratios(cls, v):
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):  # 浮動小数点誤差を考慮
            raise ValueError(f"難易度比率の合計は1.0である必要があります (現在: {total})")
        
        # 難易度は1-5の整数文字列のみ許可
        for level in v.keys():
            if level not in ['1', '2', '3', '4', '5']:
                raise ValueError(f"難易度レベルは1-5である必要があります: {level}")
        return v

class ExamGenerateRequest(BaseModel):
    """模試生成リクエスト"""
    num_questions: int = Field(..., ge=1, le=200, description="問題数")
    difficulty_ratio: Dict[str, float] = Field(..., description="難易度比率")
    tags: Optional[List[str]] = Field(default=None, description="対象タグ (省略時は全分野)")
    time_limit_min: int = Field(default=120, ge=10, le=300, description="制限時間(分)")
    
    @validator('difficulty_ratio')
    def validate_difficulty_ratio(cls, v):
        return DifficultyRatio(ratios=v).ratios

class Choice(BaseModel):
    """選択肢"""
    label: str
    body: str
    is_correct: bool

class ExamQuestion(BaseModel):
    """模試問題"""
    id: int
    question: str
    choices: List[Choice]
    difficulty: int
    tags: List[str]

class ExamGenerateResponse(BaseModel):
    """模試生成レスポンス"""
    exam_id: str
    questions: List[ExamQuestion]
    time_limit_sec: int
    metadata: Dict = Field(default_factory=dict)

# === Database Connection ===

@contextmanager
def get_db_connection():
    """SQLite接続管理"""
    conn = sqlite3.connect("data/problems.db")
    conn.row_factory = sqlite3.Row  # 辞書形式でアクセス可能
    try:
        yield conn
    finally:
        conn.close()

# === Core Logic ===

class ExamGenerator:
    """模試生成ロジック"""
    
    def __init__(self):
        self._ensure_temp_table()
    
    def _ensure_temp_table(self):
        """一時テーブル作成"""
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS temp_exam (
                    exam_id TEXT,
                    problem_id INTEGER,
                    order_index INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (exam_id, problem_id)
                )
            """)
            
            # 古い一時データ削除 (24時間経過)
            conn.execute("""
                DELETE FROM temp_exam 
                WHERE created_at < datetime('now', '-1 day')
            """)
            conn.commit()
    
    def generate_exam(self, request: ExamGenerateRequest) -> ExamGenerateResponse:
        """模試生成メイン処理"""
        start_time = time.time()
        
        # 1. 候補問題を取得
        candidate_problems = self._fetch_candidate_problems(request.tags)
        
        if len(candidate_problems) < request.num_questions:
            raise HTTPException(
                status_code=400,
                detail=f"条件に合う問題が不足しています。必要: {request.num_questions}, 利用可能: {len(candidate_problems)}"
            )
        
        # 2. 難易度比率に従って問題を選択
        selected_problems = self._select_problems_by_difficulty(
            candidate_problems, 
            request.num_questions, 
            request.difficulty_ratio
        )
        
        # 3. シャッフル
        random.shuffle(selected_problems)
        
        # 4. 一時テーブルに保存
        exam_id = str(uuid.uuid4())
        self._save_to_temp_table(exam_id, selected_problems)
        
        # 5. レスポンス構築
        questions = self._build_question_list(selected_problems)
        
        elapsed_time = (time.time() - start_time) * 1000  # ms
        
        return ExamGenerateResponse(
            exam_id=exam_id,
            questions=questions,
            time_limit_sec=request.time_limit_min * 60,
            metadata={
                "generation_time_ms": round(elapsed_time, 2),
                "actual_difficulty_distribution": self._calculate_actual_distribution(selected_problems),
                "total_candidates": len(candidate_problems)
            }
        )
    
    def _fetch_candidate_problems(self, tags: Optional[List[str]]) -> List[Dict]:
        """条件に合う候補問題を取得"""
        with get_db_connection() as conn:
            if tags:
                # タグ条件がある場合
                placeholders = ','.join(['?' for _ in tags])
                query = f"""
                    SELECT p.*, GROUP_CONCAT(c.label) as choice_labels,
                           GROUP_CONCAT(c.body) as choice_bodies,
                           GROUP_CONCAT(c.is_correct) as choice_corrects
                    FROM problem p
                    LEFT JOIN choice c ON p.id = c.problem_id
                    WHERE p.tags REGEXP ?
                    GROUP BY p.id
                    ORDER BY p.id
                """
                # SQLite REGEXPは簡易実装として、タグをOR条件で結合
                tag_pattern = '|'.join(tags)
                cursor = conn.execute(query, (tag_pattern,))
            else:
                # 全問題対象
                query = """
                    SELECT p.*, GROUP_CONCAT(c.label) as choice_labels,
                           GROUP_CONCAT(c.body) as choice_bodies,
                           GROUP_CONCAT(c.is_correct) as choice_corrects
                    FROM problem p
                    LEFT JOIN choice c ON p.id = c.problem_id
                    GROUP BY p.id
                    ORDER BY p.id
                """
                cursor = conn.execute(query)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def _select_problems_by_difficulty(
        self, 
        candidates: List[Dict], 
        num_questions: int, 
        difficulty_ratio: Dict[str, float]
    ) -> List[Dict]:
        """難易度比率に従って問題選択"""
        
        # 難易度別に分類
        by_difficulty = {}
        for problem in candidates:
            diff = str(problem['difficulty'])
            if diff not in by_difficulty:
                by_difficulty[diff] = []
            by_difficulty[diff].append(problem)
        
        selected = []
        
        for difficulty_str, ratio in difficulty_ratio.items():
            target_count = round(num_questions * ratio)
            available = by_difficulty.get(difficulty_str, [])
            
            if len(available) < target_count:
                # 不足分は他の難易度から補完
                selected.extend(available)
            else:
                # ランダムサンプリング
                selected.extend(random.sample(available, target_count))
        
        # 不足分を残り候補から補完
        if len(selected) < num_questions:
            remaining_candidates = [p for p in candidates if p not in selected]
            shortage = num_questions - len(selected)
            if len(remaining_candidates) >= shortage:
                selected.extend(random.sample(remaining_candidates, shortage))
            else:
                selected.extend(remaining_candidates)
        
        return selected[:num_questions]
    
    def _save_to_temp_table(self, exam_id: str, problems: List[Dict]):
        """一時テーブルに保存"""
        with get_db_connection() as conn:
            for idx, problem in enumerate(problems):
                conn.execute("""
                    INSERT INTO temp_exam (exam_id, problem_id, order_index)
                    VALUES (?, ?, ?)
                """, (exam_id, problem['id'], idx))
            conn.commit()
    
    def _build_question_list(self, problems: List[Dict]) -> List[ExamQuestion]:
        """レスポンス用問題リスト構築"""
        questions = []
        
        for problem in problems:
            # 選択肢を解析
            choices = []
            if problem['choice_labels']:
                labels = problem['choice_labels'].split(',')
                bodies = problem['choice_bodies'].split(',')
                corrects = problem['choice_corrects'].split(',')
                
                for label, body, correct in zip(labels, bodies, corrects):
                    choices.append(Choice(
                        label=label.strip(),
                        body=body.strip(),
                        is_correct=correct.strip() == '1'
                    ))
            
            # タグを解析
            tags = problem['tags'].split(',') if problem['tags'] else []
            
            questions.append(ExamQuestion(
                id=problem['id'],
                question=problem['question'],
                choices=choices,
                difficulty=problem['difficulty'],
                tags=[tag.strip() for tag in tags]
            ))
        
        return questions
    
    def _calculate_actual_distribution(self, problems: List[Dict]) -> Dict[str, float]:
        """実際の難易度分布を計算"""
        total = len(problems)
        if total == 0:
            return {}
        
        counts = {}
        for problem in problems:
            diff = str(problem['difficulty'])
            counts[diff] = counts.get(diff, 0) + 1
        
        return {diff: count / total for diff, count in counts.items()}

# === API Router ===

router = APIRouter(prefix="/exam", tags=["exam"])
generator = ExamGenerator()

@router.post("/generate", response_model=ExamGenerateResponse)
async def generate_exam(request: ExamGenerateRequest):
    """
    模試問題セット生成
    
    指定されたパラメータに基づいて模試用の問題セットを生成します。
    - 難易度比率に従った問題選択
    - ランダムシャッフル
    - 一時テーブルへの保存
    """
    try:
        return generator.generate_exam(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模試生成エラー: {str(e)}")

# === Utility Endpoints ===

@router.get("/stats")
async def get_exam_stats():
    """問題データベースの統計情報"""
    with get_db_connection() as conn:
        # 難易度別問題数
        difficulty_stats = {}
        cursor = conn.execute("""
            SELECT difficulty, COUNT(*) as count 
            FROM problem 
            GROUP BY difficulty 
            ORDER BY difficulty
        """)
        for row in cursor:
            difficulty_stats[str(row['difficulty'])] = row['count']
        
        # タグ別問題数 (上位10)
        tag_stats = {}
        cursor = conn.execute("""
            SELECT tags, COUNT(*) as count 
            FROM problem 
            WHERE tags IS NOT NULL 
            GROUP BY tags 
            ORDER BY count DESC 
            LIMIT 10
        """)
        for row in cursor:
            tag_stats[row['tags']] = row['count']
        
        # 総問題数
        total_count = conn.execute("SELECT COUNT(*) as count FROM problem").fetchone()['count']
        
        return {
            "total_problems": total_count,
            "difficulty_distribution": difficulty_stats,
            "popular_tags": tag_stats
        }

@router.delete("/temp/{exam_id}")
async def delete_temp_exam(exam_id: str):
    """一時テーブルから指定された模試データを削除"""
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM temp_exam WHERE exam_id = ?", (exam_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="指定された模試IDが見つかりません")
        
        return {"message": f"模試 {exam_id} を削除しました", "deleted_rows": cursor.rowcount}