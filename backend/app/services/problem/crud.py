"""
CRUD operations for problems
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.problem import Problem, Choice
from app.models.schemas import ProblemCreate

class ProblemCRUD:
    """CRUD service for problems"""
    
    async def get_problems(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        difficulty: Optional[int] = None,
        tags: Optional[str] = None
    ) -> List[Problem]:
        """Get problems with filters"""
        query = db.query(Problem)
        
        if difficulty:
            query = query.filter(Problem.difficulty == difficulty)
        
        if tags:
            query = query.filter(Problem.tags.contains(tags))
        
        return query.offset(skip).limit(limit).all()
    
    async def get_problem(self, db: Session, problem_id: int) -> Optional[Problem]:
        """Get single problem by ID"""
        return db.query(Problem).filter(Problem.id == problem_id).first()
    
    async def create_problem(self, db: Session, problem: ProblemCreate) -> Problem:
        """Create new problem"""
        db_problem = Problem(
            question=problem.question,
            answer=problem.answer,
            explanation=problem.explanation,
            difficulty=problem.difficulty,
            tags=problem.tags,
            source_url=problem.source_url
        )
        
        db.add(db_problem)
        db.commit()
        db.refresh(db_problem)
        
        # Add choices
        for choice_data in problem.choices:
            db_choice = Choice(
                problem_id=db_problem.id,
                label=choice_data.label,
                body=choice_data.body,
                is_correct=choice_data.is_correct
            )
            db.add(db_choice)
        
        db.commit()
        db.refresh(db_problem)
        
        return db_problem
    
    async def delete_problem(self, db: Session, problem_id: int) -> bool:
        """Delete problem"""
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
        if problem:
            db.delete(problem)
            db.commit()
            return True
        return False

# Global instance
_problem_crud = ProblemCRUD()

async def get_problem_crud() -> ProblemCRUD:
    """Dependency injection for FastAPI"""
    return _problem_crud