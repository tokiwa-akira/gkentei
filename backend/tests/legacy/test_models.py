"""
G検定学習アプリ モデルテスト
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Problem, Choice, AnswerLog


@pytest.fixture(scope="function")
def db_session():
    """テスト用インメモリSQLiteセッション"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


def test_create_problem(db_session):
    """問題テーブル作成テスト"""
    problem = Problem(
        question="機械学習における教師あり学習の説明として最も適切なものはどれか？",
        answer="正解は選択肢Aです",
        explanation="教師あり学習は入力と正解ラベルの組み合わせから学習する手法です",
        difficulty=2,
        tags="機械学習,教師あり学習",
        source_url="https://example.com/ml-basics"
    )
    
    db_session.add(problem)
    db_session.commit()
    
    # 取得確認
    saved_problem = db_session.query(Problem).first()
    assert saved_problem.id == problem.id
    assert saved_problem.question == problem.question
    assert saved_problem.difficulty == 2
    assert isinstance(saved_problem.created_at, datetime)


def test_create_choices_with_problem(db_session):
    """問題と選択肢の関連テスト"""
    problem = Problem(
        question="テスト問題",
        answer="選択肢A",
        difficulty=1
    )
    db_session.add(problem)
    db_session.flush()  # IDを取得するためflush
    
    choices = [
        Choice(problem_id=problem.id, label="A", body="正解の選択肢", is_correct=True),
        Choice(problem_id=problem.id, label="B", body="不正解の選択肢1", is_correct=False),
        Choice(problem_id=problem.id, label="C", body="不正解の選択肢2", is_correct=False),
        Choice(problem_id=problem.id, label="D", body="不正解の選択肢3", is_correct=False),
    ]
    
    for choice in choices:
        db_session.add(choice)
    db_session.commit()
    
    # リレーション確認
    saved_problem = db_session.query(Problem).first()
    assert len(saved_problem.choices) == 4
    
    correct_choice = [c for c in saved_problem.choices if c.is_correct][0]
    assert correct_choice.label == "A"
    assert correct_choice.body == "正解の選択肢"


def test_create_answer_log(db_session):
    """回答ログテスト"""
    problem = Problem(
        question="テスト問題",
        answer="テスト回答",
        difficulty=1
    )
    db_session.add(problem)
    db_session.flush()
    
    answer_log = AnswerLog(
        problem_id=problem.id,
        is_correct=True,
        time_ms=5500  # 5.5秒
    )
    db_session.add(answer_log)
    db_session.commit()
    
    # 取得確認
    saved_log = db_session.query(AnswerLog).first()
    assert saved_log.problem_id == problem.id
    assert saved_log.is_correct is True
    assert saved_log.time_ms == 5500
    assert isinstance(saved_log.answered_at, datetime)
    
    # リレーション確認
    assert saved_log.problem.question == "テスト問題"


def test_cascade_delete(db_session):
    """カスケード削除テスト"""
    # 問題作成
    problem = Problem(question="削除テスト問題", answer="テスト", difficulty=1)
    db_session.add(problem)
    db_session.flush()
    
    # 選択肢と回答ログ作成
    choice = Choice(problem_id=problem.id, label="A", body="選択肢", is_correct=True)
    log = AnswerLog(problem_id=problem.id, is_correct=True, time_ms=1000)
    
    db_session.add(choice)
    db_session.add(log)
    db_session.commit()
    
    # 削除前の確認
    assert db_session.query(Problem).count() == 1
    assert db_session.query(Choice).count() == 1
    assert db_session.query(AnswerLog).count() == 1
    
    # 問題削除（カスケードで選択肢・ログも削除されるはず）
    db_session.delete(problem)
    db_session.commit()
    
    # 削除後の確認
    assert db_session.query(Problem).count() == 0
    assert db_session.query(Choice).count() == 0
    assert db_session.query(AnswerLog).count() == 0


def test_table_creation():
    """テーブル作成・削除のサイクルテスト"""
    engine = create_engine("sqlite:///:memory:")
    
    # テーブル作成
    Base.metadata.create_all(engine)
    
    # テーブル存在確認
    table_names = engine.table_names()
    expected_tables = {"problems", "choices", "answer_logs"}
    assert expected_tables.issubset(set(table_names))
    
    # テーブル削除
    Base.metadata.drop_all(engine)
    
    # テーブル削除確認
    table_names_after = engine.table_names()
    assert len(table_names_after) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])