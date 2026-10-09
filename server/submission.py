from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import redis
from rq import Queue

from database import UserDB, SubmissionDB, ProblemDB
from auth import get_db, get_current_user

router = APIRouter(prefix="/api/submissions", tags=["Submissions"])

# Initialize Redis queue connection
redis_conn = redis.Redis(host='localhost', port=6379)
task_queue = Queue('judge_queue', connection=redis_conn)

class SubmitPayload(BaseModel):
    problem_id: int
    code: str
    language: str

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

    # 1. Insert as Pending
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

    # 2. Push to Redis queue (pass only IDs to the worker, not the whole code)
    task_queue.enqueue(
        "worker.evaluate_submission", 
        submission_id=submission.id,
        job_timeout="10s"
    )

    # 3. Return immediately
    return {
        "id": submission.id,
        "status": submission.status,
        "message": "Submission queued."
    }

# New route for Babel-CP to poll the result
@router.get("/{submission_id}")
async def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    submission = db.query(SubmissionDB).filter(SubmissionDB.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    return {
        "id": submission.id,
        "status": submission.status,
        # You will need to add these fields to SubmissionDB if they aren't there yet
        "time": getattr(submission, 'execution_time', None),
        "compile_output": getattr(submission, 'compile_output', None)
    }
