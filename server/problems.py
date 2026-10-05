from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import ProblemDB
from auth import get_db, get_current_user

import os

router = APIRouter(prefix="/api/problems", tags=["Problems"])

class ProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    subject: str
    difficulty: str
    time_limit: float
    memory_limit: int

    class Config:
        from_attributes = True

@router.get("", response_model=list[ProblemResponse])
async def get_problems(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(ProblemDB).all()


@router.get("/{problem_id}/subject")
async def get_problem_subject(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    problem = db.query(ProblemDB).filter(ProblemDB.id == problem_id).first()
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Problem not found"
        )
        
    file_path = problem.subject 
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Subject file missing on server"
        )
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return {"content": content}
