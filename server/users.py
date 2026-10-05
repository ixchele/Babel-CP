from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import UserDB
from auth import get_db, get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])

class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    score: int

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    users = db.query(UserDB).order_by(UserDB.score.desc()).limit(100).all()
    
    leaderboard = []
    for index, user in enumerate(users, start=1):
        leaderboard.append({
            "rank": index,
            "username": user.username,
            "score": user.score or 0
        })
        
    return leaderboard


@router.get("/me")
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_user = db.query(UserDB).filter(UserDB.username == current_user.username).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    higher_scores = db.query(UserDB).filter(UserDB.score > db_user.score).count()
    rank = higher_scores + 1
    
    return {
        "username": db_user.username,
        "score": db_user.score or 0,
        "rank": rank
    }
