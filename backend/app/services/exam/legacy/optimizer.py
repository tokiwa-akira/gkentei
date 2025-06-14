"""
模試API パフォーマンス最適化
- インデックス作成
- クエリ最適化  
- キャッシュ機能
"""

import sqlite3
import hashlib
import json
from typing import Dict, List, Optional
from functools import lru_cache
from contextlib import contextmanager
import logging

# === Database Optimization ===

def create_performance_indexes():
    """パフォーマンス向上用インデックス作成"""
    with get_db_connection() as conn:
        # 難易度検索用インデックス
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_problem_difficulty 
            ON problem(difficulty)
        """)
        
        # タグ検索用インデックス (FTS5使用)
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS problem_fts 
            USING fts5(tags, content='problem', content_rowid='id')
        """)
        
        # problem_ftsテーブルにデータを投入
        conn.execute("""
            INSERT OR REPLACE INTO problem_fts(rowid, tags)
            SELECT id, tags FROM problem WHERE tags IS NOT NULL
        """)
        
        # 複合インデックス
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_problem_difficulty_created 
            ON problem(difficulty, created_at)
        """)
        
        # 選択肢テーブル用インデックス
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_choice_problem_id 
            ON choice(problem_id)
        """)
        
        # 一時テーブル用インデックス
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_temp_exam_id 
            ON temp_exam(exam_id)
        """)
        
        conn.commit()
        logging.info("パフォーマンス用インデックスを作成しました")

# === Optimized Query Builder ===

class OptimizedQueryBuilder:
    """最適化されたクエリビルダー"""
    
    @staticmethod
    def build_candidate_query(tags: Optional[List[str]] = None) -> tuple:
        """候補問題取得用最適化クエリ"""
        
        if tags:
            # FTS5を使用したタグ検索
            query = """
                WITH filtered_problems AS (
                    SELECT p.id, p.question, p.answer, p.explanation, 
                           p.difficulty, p.tags, p.source_url, p.created_at
                    FROM problem p
                    JOIN problem_fts fts ON p.id = fts.rowid
                    WHERE problem_fts MATCH ?
                ),
                problems_with_choices AS (
                    SELECT fp.*,
                           json_group_array(
                               json_object(
                                   'label', c.label,
                                   'body', c.body,
                                   'is_correct', c.is_correct
                               )
                           ) as choices_json
                    FROM filtered_problems fp
                    LEFT JOIN choice c ON fp.id = c.problem_id
                    GROUP BY fp.id
                )
                SELECT * FROM problems_with_choices
                ORDER BY difficulty, id
            """
            
            # FTS5クエリ形式に変換
            fts_query = ' OR '.join(f'tags:{tag}' for tag in tags)
            params = (fts_query,)
            
        else:
            # 全問題対象（最適化版）
            query = """
                WITH problems_with_choices AS (
                    SELECT p.id, p.question, p.answer, p.explanation,
                           p.difficulty, p.tags, p.source_url, p.created_at,
                           json_group_array(
                               json_object(
                                   'label', c.label,
                                   'body', c.body,
                                   'is_correct', c.is_correct
                               )
                           ) as choices_json
                    FROM problem p
                    LEFT JOIN choice c ON p.id = c.problem_id
                    GROUP BY p.id
                )
                SELECT * FROM problems_with_choices
                ORDER BY difficulty, id
            """
            params = ()
        
        return query, params
    
    @staticmethod
    def build_difficulty_distribution_query() -> str:
        """難易度分布取得用クエリ"""
        return """
            SELECT difficulty, COUNT(*) as count
            FROM problem
            GROUP BY difficulty
            ORDER BY difficulty
        """
    
    @staticmethod  
    def build_tag_stats_query(limit: int = 20) -> tuple:
        """タグ統計取得用クエリ"""
        query = """
            WITH tag_splits AS (
                SELECT TRIM(value) as tag
                FROM problem, json_each('["' || REPLACE(tags, ',', '","') || '"]')
                WHERE tags IS NOT NULL
            )
            SELECT tag, COUNT(*) as count
            FROM tag_splits
            WHERE tag != ''
            GROUP BY tag
            ORDER BY count DESC
            LIMIT ?
        """
        return query, (limit,)

# === Cache Layer ===

class ExamCache:
    """模試生成結果キャッシュ"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache = {}
    
    def _generate_cache_key(self, request_dict: Dict) -> str:
        """リクエスト内容からキャッシュキーを生成"""
        # tagsをソートして順序に依存しないキーにする
        normalized = request_dict.copy()
        if normalized.get('tags'):
            normalized['tags'] = sorted(normalized['tags'])
        
        # JSON文字列からハッシュ生成
        json_str = json.dumps(normalized, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def get(self, request_dict: Dict) -> Optional[List[Dict]]:
        """キャッシュから候補問題を取得"""
        cache_key = self._generate_cache_key(request_dict)
        return self._cache.get(cache_key)
    
    def set(self, request_dict: Dict, candidates: List[Dict]):
        """候補問題をキャッシュに保存"""
        if len(self._cache) >= self.max_size:
            # LRU的な削除（簡易版）
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        cache_key = self._generate_cache_key(request_dict)
        self._cache[cache_key] = candidates.copy()
    
    def clear(self):
        """キャッシュクリア"""
        self._cache.clear()

# === Optimized Exam Generator ===

class OptimizedExamGenerator(ExamGenerator):
    """最適化された模試生成器"""
    
    def __init__(self):
        super().__init__()
        self.query_builder = OptimizedQueryBuilder()
        self.cache = ExamCache()
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """必要なインデックスを確認・作成"""
        try:
            create_performance_indexes()
        except Exception as e:
            logging.warning(f"インデックス作成エラー: {e}")
    
    def _fetch_candidate_problems(self, tags: Optional[List[str]]) -> List[Dict]:
        """最適化された候補問題取得"""
        
        # キャッシュ確認
        cache_key_dict = {'tags': tags}
        cached_result = self.cache.get(cache_key_dict)
        if cached_result:
            logging.info("キャッシュから候補問題を取得")
            return cached_result
        
        # 最適化クエリ実行
        query, params = self.query_builder.build_candidate_query(tags)
        
        with get_db_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        # 結果をパース
        candidates = []
        for row in rows:
            row_dict = dict(row)
            
            # JSON形式の選択肢をパース
            if row_dict['choices_json']:
                try:
                    choices_data = json.loads(row_dict['choices_json'])
                    
                    # 選択肢を従来形式に変換
                    labels, bodies, corrects = [], [], []
                    for choice in choices_data:
                        if choice['label']:  # nullチェック
                            labels.append(choice['label'])
                            bodies.append(choice['body'])
                            corrects.append('1' if choice['is_correct'] else '0')
                    
                    row_dict['choice_labels'] = ','.join(labels)
                    row_dict['choice_bodies'] = ','.join(bodies)
                    row_dict['choice_corrects'] = ','.join(corrects)
                except json.JSONDecodeError:
                    # フォールバック
                    row_dict['choice_labels'] = ''
                    row_dict['choice_bodies'] = ''
                    row_dict['choice_corrects'] = ''
            
            candidates.append(row_dict)
        
        # キャッシュに保存
        self.cache.set(cache_key_dict, candidates)
        
        logging.info(f"候補問題 {len(candidates)} 件を取得")
        return candidates
    
    def _select_problems_by_difficulty_optimized(
        self, 
        candidates: List[Dict], 
        num_questions: int, 
        difficulty_ratio: Dict[str, float]
    ) -> List[Dict]:
        """最適化された難易度別問題選択"""
        
        # 事前に難易度別インデックスを作成
        by_difficulty = {}
        for i, problem in enumerate(candidates):
            diff = str(problem['difficulty'])
            if diff not in by_difficulty:
                by_difficulty[diff] = []
            by_difficulty[diff].append((i, problem))
        
        selected_indices = set()
        selected_problems = []
        
        # 難易度比率に基づく選択（改良版）
        remaining_questions = num_questions
        
        for difficulty_str, ratio in sorted(difficulty_ratio.items()):
            if remaining_questions <= 0:
                break
                
            target_count = max(1, round(num_questions * ratio))
            target_count = min(target_count, remaining_questions)
            
            available_items = [
                item for item in by_difficulty.get(difficulty_str, [])
                if item[0] not in selected_indices
            ]
            
            if available_items:
                # ランダムサンプリング
                import random
                sample_count = min(target_count, len(available_items))
                sampled_items = random.sample(available_items, sample_count)
                
                for idx, problem in sampled_items:
                    selected_indices.add(idx)
                    selected_problems.append(problem)
                    remaining_questions -= 1
        
        # 不足分を補完
        if remaining_questions > 0:
            remaining_items = [
                (i, p) for i, p in enumerate(candidates)
                if i not in selected_indices
            ]
            
            if remaining_items:
                import random
                supplement_count = min(remaining_questions, len(remaining_items))
                supplemented = random.sample(remaining_items, supplement_count)
                
                for idx, problem in supplemented:
                    selected_problems.append(problem)
        
        return selected_problems[:num_questions]

# === Performance Monitoring ===

class PerformanceMonitor:
    """パフォーマンス監視"""
    
    @staticmethod
    def measure_query_performance():
        """クエリパフォーマンス測定"""
        with get_db_connection() as conn:
            # EXPLAIN QUERY PLAN で実行計画を確認
            queries_to_test = [
                "SELECT * FROM problem WHERE difficulty = 2",
                "SELECT * FROM problem_fts WHERE problem_fts MATCH 'tags:数学'",
                "SELECT COUNT(*) FROM problem GROUP BY difficulty"
            ]
            
            results = {}
            for query in queries_to_test:
                start_time = time.time()
                try:
                    cursor = conn.execute(f"EXPLAIN QUERY PLAN {query}")
                    plan = cursor.fetchall()
                    
                    cursor = conn.execute(query)
                    rows = cursor.fetchall()
                    
                    elapsed = (time.time() - start_time) * 1000
                    results[query] = {
                        'execution_time_ms': elapsed,
                        'rows_returned': len(rows),
                        'query_plan': [dict(row) for row in plan]
                    }
                except Exception as e:
                    results[query] = {'error': str(e)}
            
            return results

# === New Router with Optimizations ===

def create_optimized_router():
    """最適化された模試APIルーター"""
    from fastapi import APIRouter
    
    router = APIRouter(prefix="/exam", tags=["exam"])
    generator = OptimizedExamGenerator()
    monitor = PerformanceMonitor()
    
    @router.post("/generate", response_model=ExamGenerateResponse)
    async def generate_exam_optimized(request: ExamGenerateRequest):
        """最適化された模試生成"""
        import time
        start_time = time.time()
        
        try:
            result = generator.generate_exam(request)
            
            # パフォーマンス情報を追加
            elapsed_ms = (time.time() - start_time) * 1000
            result.metadata['total_generation_time_ms'] = round(elapsed_ms, 2)
            result.metadata['cache_size'] = len(generator.cache._cache)
            
            return result
            
        except Exception as e:
            logging.error(f"模試生成エラー: {e}")
            raise HTTPException(status_code=500, detail=f"模試生成エラー: {str(e)}")
    
    @router.get("/performance")
    async def get_performance_stats():
        """パフォーマンス統計"""
        return monitor.measure_query_performance()
    
    @router.post("/cache/clear")
    async def clear_cache():
        """キャッシュクリア"""
        generator.cache.clear()
        return {"message": "キャッシュをクリアしました"}
    
    return router

# === Database Migration ===

def migrate_to_optimized_schema():
    """最適化スキーマへのマイグレーション"""
    with get_db_connection() as conn:
        # バージョン管理テーブル
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 現在のバージョン確認
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        current_version = cursor.fetchone()[0] or 0
        
        migrations = [
            # v1: パフォーマンスインデックス
            (1, create_performance_indexes),
            # v2: 将来の拡張用
        ]
        
        for version, migration_func in migrations:
            if version > current_version:
                try:
                    migration_func()
                    conn.execute(
                        "INSERT INTO schema_version (version) VALUES (?)", 
                        (version,)
                    )
                    conn.commit()
                    logging.info(f"マイグレーション v{version} 完了")
                except Exception as e:
                    conn.rollback()
                    logging.error(f"マイグレーション v{version} 失敗: {e}")
                    raise

if __name__ == "__main__":
    # 最適化の適用
    migrate_to_optimized_schema()
    print("最適化設定が完了しました")