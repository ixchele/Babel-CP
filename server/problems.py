from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import ProblemDB
from auth import get_db, get_current_user

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
