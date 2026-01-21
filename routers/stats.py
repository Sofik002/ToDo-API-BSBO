from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from typing import List
from datetime import datetime

from database import get_db
from models.task import Task
from schemas import TimingStatsResponse
from crud import TaskCRUD

router = APIRouter(
    prefix="/stats",
    tags=["statistics"]
)

# ---------------- GET ОБЩИЕ СТАТИСТИКИ ----------------
@router.get("/", response_model=dict)
async def get_tasks_stats(db: AsyncSession = Depends(get_db)) -> dict:
    total_result = await db.execute(select(func.count(Task.id)))
    total_tasks = total_result.scalar() or 0

    quadrant_result = await db.execute(
        select(Task.quadrant, func.count(Task.id).label("count")).group_by(Task.quadrant)
    )
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for row in quadrant_result.all():
        if row.quadrant in ["Q1", "Q2", "Q3", "Q4"]:
            by_quadrant[row.quadrant] = row.count

    status_result = await db.execute(
        select(
            func.count(case((Task.completed == True, 1))).label("completed"),
            func.count(case((Task.completed == False, 1))).label("pending")
        )
    )
    status_row = status_result.one()
    by_status = {
        "completed": status_row.completed,
        "pending": status_row.pending
    }

    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }

# ---------------- GET СТАТИСТИКА ПО ДЕДЛАЙНАМ ----------------
@router.get("/stats/deadlines")
async def get_deadline_stats(
    db: AsyncSession = Depends(get_db)
) -> list[dict]:

    result = await db.execute(
        select(Task).where(
            Task.deadline_at.isnot(None),
            Task.completed.is_(False)
        )
    )
    tasks = result.scalars().all()

    now = datetime.utcnow()  # 🔥 ВАЖНО: naive datetime

    response = []

    for task in tasks:
        delta = task.deadline_at - now
        days_until_deadline = delta.days

        status = "срочно" if delta.total_seconds() >= 0 else "не срочно"

        response.append({
            "id": task.id,
            "title": task.title,
            "deadline_at": task.deadline_at,
            "days_until_deadline": days_until_deadline,
            "status": status
        })

    return response