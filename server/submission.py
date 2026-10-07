from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import asyncio

from database import UserDB, SubmissionDB, ResolveDB, ProblemDB
from auth import get_db, get_current_user

router = APIRouter(prefix="/api/submissions", tags=["Submissions"])

class SubmitPayload(BaseModel):
    problem_id: int
    code: str
    language: str

async def mock_judge_evaluator(code: str, problem_id: int) -> dict:
    await asyncio.sleep(10.0)
    
    lower_code = code.lower()
    if "error" in lower_code:
        return {
            "status": "Compilation Error", 
            "time": "0.00s", 
            "compile_output": "Mock error: syntax error detected.",
            "logs": "decet error flan flania",
        }
    
    stripped_code = lower_code.replace(" ", "")
    if "while(1)" in stripped_code or "while(true)" in stripped_code:
        return {
            "status": "Time Limit Exceeded", 
            "time": "5.00s",
            "logs": "infinit loop",
        }
    
    return {
        "status": "Accepted", 
        "time": "0.02s", 
        "stdout": "All test cases passed.",
        "logs": "All good"
    }

@router.post("/")
async def submit_code(
    payload: SubmitPayload,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = db.query(UserDB).filter(UserDB.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    problem = db.query(ProblemDB).filter(ProblemDB.id == payload.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    submission = SubmissionDB(
        id_user=user.id,
        id_problem=payload.problem_id,
        code_submited=payload.code,
        language=payload.language,
        status="Pending"
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    eval_result = await mock_judge_evaluator(payload.code, payload.problem_id)
    submission.status = eval_result["status"]
    
    if eval_result["status"] == "Accepted":
        already_resolved = db.query(ResolveDB).filter(
            ResolveDB.id_user == user.id,
            ResolveDB.id_problem == payload.problem_id
        ).first()
        
        if not already_resolved:
            failed_attempts = db.query(SubmissionDB).filter(
                SubmissionDB.id_user == user.id,
                SubmissionDB.id_problem == payload.problem_id,
                SubmissionDB.status != "Accepted",
                SubmissionDB.id != submission.id
            ).count()

            base_points = problem.base_points or 0
            penalty = int(base_points * 0.10 * failed_attempts)
            max_penalty = int(base_points * 0.50)
            
            points_earned = base_points - min(penalty, max_penalty)
            user.score = (user.score or 0) + points_earned
            
            new_resolve = ResolveDB(
                id_user=user.id,
                id_problem=payload.problem_id,
                number_of_tries=failed_attempts + 1,
                points=points_earned
            )
            db.add(new_resolve)

    db.commit()

    return {
        "id": submission.id,
        "status": submission.status,
        "time": eval_result.get("time"),
        "stdout": eval_result.get("stdout"),
        "compile_output": eval_result.get("compile_output")
    }
