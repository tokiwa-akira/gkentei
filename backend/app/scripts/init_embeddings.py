#!/usr/bin/env python3
"""
G検定問題文をChromaDBにEmbeddingとして登録するスクリプト

使用方法:
    python ingest_embeddings.py [--reset] [--batch-size 100]
"""

import sqlite3
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmbeddingIngestor:
    def __init__(
        self, 
        db_path: str = "./data/problems.db",
        chroma_path: str = "./data/chroma",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Args:
            db_path: SQLiteデータベースのパス
            chroma_path: ChromaDBデータディレクトリのパス  
            model_name: Embeddingモデル名
        """
        self.db_path = Path(db_path)
        self.chroma_path = Path(chroma_path)
        self.model_name = model_name
        
        # ChromaDBクライアント初期化
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Embeddingモデル初期化
        logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Collection取得/作成
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """ChromaDB Collection取得または作成"""
        try:
            collection = self.chroma_client.get_collection("problems")
            logger.info("Existing 'problems' collection found")
        except Exception:
            collection = self.chroma_client.create_collection(
                name="problems",
                metadata={"description": "G検定問題文のEmbedding"}
            )
            logger.info("Created new 'problems' collection")
        
        return collection
    
    def fetch_problems_from_db(self) -> List[Dict[str, Any]]:
        """SQLiteから問題データを取得"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        logger.info(f"Fetching problems from {self.db_path}")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # 辞書形式でアクセス可能
            cursor = conn.cursor()
            
            # 問題文とメタデータを取得
            query = """
            SELECT 
                id, 
                question, 
                answer, 
                difficulty, 
                tags, 
                source_url,
                created_at
            FROM problems 
            WHERE question IS NOT NULL AND question != ''
            ORDER BY id
            """
            
            cursor.execute(query)
            problems = [dict(row) for row in cursor.fetchall()]
            
        logger.info(f"Fetched {len(problems)} problems")
        return problems
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """テキストリストからEmbeddingを生成"""
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.embedding_model.encode(
            texts, 
            convert_to_tensor=False,
            show_progress_bar=True
        )
        return embeddings.tolist()
    
    def prepare_snippets(self, questions: List[str], max_length: int = 150) -> List[str]:
        """検索結果表示用のスニペットを生成"""
        snippets = []
        for question in questions:
            if len(question) <= max_length:
                snippets.append(question)
            else:
                # 文末で切り詰め
                truncated = question[:max_length].rsplit('。', 1)[0]
                if len(truncated) < 50:  # 短すぎる場合は文字数で切り詰め
                    truncated = question[:max_length]
                snippets.append(truncated + "...")
        
        return snippets
    
    def upsert_to_chroma(
        self, 
        problems: List[Dict[str, Any]], 
        batch_size: int = 100
    ) -> None:
        """ChromaDBに問題データをバッチでupsert"""
        logger.info(f"Upserting {len(problems)} problems to ChromaDB")
        
        # バッチ処理
        for i in tqdm(range(0, len(problems), batch_size), desc="Upserting batches"):
            batch = problems[i:i + batch_size]
            
            # バッチデータ準備
            ids = [str(problem['id']) for problem in batch]
            questions = [problem['question'] for problem in batch]
            snippets = self.prepare_snippets(questions)
            
            # メタデータ準備
            metadatas = []
            for problem in batch:
                metadata = {
                    'difficulty': problem.get('difficulty', 1),
                    'tags': problem.get('tags', ''),
                    'source_url': problem.get('source_url', ''),
                    'created_at': problem.get('created_at', ''),
                    'snippet': snippets[batch.index(problem)]
                }
                metadatas.append(metadata)
            
            # Embedding生成
            embeddings = self.generate_embeddings(questions)
            
            # ChromaDBにupsert
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=questions,
                metadatas=metadatas
            )
        
        logger.info("Upsert completed successfully")
    
    def reset_collection(self) -> None:
        """Collectionを削除して再作成"""
        logger.warning("Resetting 'problems' collection")
        try:
            self.chroma_client.delete_collection("problems")
        except Exception as e:
            logger.warning(f"Could not delete collection: {e}")
        
        self.collection = self._get_or_create_collection()
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Collection統計情報を取得"""
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': 'problems',
            'embedding_model': self.model_name,
            'chroma_path': str(self.chroma_path)
        }

def main():
    parser = argparse.ArgumentParser(description='Ingest G検定問題文 to ChromaDB')
    parser.add_argument(
        '--reset', 
        action='store_true',
        help='Reset collection before ingesting'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for upsert (default: 100)'
    )
    parser.add_argument(
        '--db-path',
        default='./data/problems.db',
        help='SQLite database path'
    )
    parser.add_argument(
        '--chroma-path',
        default='./data/chroma',
        help='ChromaDB storage path'
    )
    parser.add_argument(
        '--model',
        default='sentence-transformers/all-MiniLM-L6-v2',
        help='Embedding model name'
    )
    
    args = parser.parse_args()
    
    try:
        # Ingestor初期化
        ingestor = EmbeddingIngestor(
            db_path=args.db_path,
            chroma_path=args.chroma_path,
            model_name=args.model
        )
        
        # Collection リセット (必要に応じて)
        if args.reset:
            ingestor.reset_collection()
        
        # 問題データ取得
        problems = ingestor.fetch_problems_from_db()
        
        if not problems:
            logger.warning("No problems found in database")
            return
        
        # ChromaDBにupsert
        ingestor.upsert_to_chroma(problems, batch_size=args.batch_size)
        
        # 統計情報表示
        stats = ingestor.get_collection_stats()
        logger.info("Ingestion completed!")
        logger.info(f"Collection stats: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise

if __name__ == "__main__":
    main()