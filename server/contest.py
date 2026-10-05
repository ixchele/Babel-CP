from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/contest", tags=["Contest"])

state = {
    "end_time": None
}

@router.get("/status")
async def get_status():
    if not state["end_time"]:
        return {"is_active": False, "remaining_seconds": 0}

    time_left = state["end_time"] - datetime.now()
    seconds = int(time_left.total_seconds())

    if seconds <= 0:
        state["end_time"] = None
        return {"is_active": False, "remaining_seconds": 0}

    return {"is_active": True, "remaining_seconds": seconds}

from auth import get_current_admin

@router.post("/start")
async def start_contest(
    duration_minutes: int = 120,
    admin_user = Depends(get_current_admin) 
):
    state["end_time"] = datetime.now() + timedelta(minutes=duration_minutes)
    return {"status": "started", "started_by": admin_user.username}
