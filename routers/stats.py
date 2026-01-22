# routers/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from typing import List
from datetime import datetime

from database import get_async_session  # ИСПРАВЛЕН ИМПОРТ
from models.task import Task
from schemas import TimingStatsResponse
from dependencies import get_current_user

router = APIRouter(
    prefix="/stats",
    tags=["statistics"]
)

# ---------------- GET ОБЩИЕ СТАТИСТИКИ (с учетом прав) ----------------
@router.get("/", response_model=dict)
async def get_tasks_stats(
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user = Depends(get_current_user)
) -> dict:
    # Админ видит все задачи, пользователь - только свои
    if current_user.role.value == "admin":
        total_result = await db.execute(select(func.count(Task.id)))
        total_tasks = total_result.scalar() or 0

        quadrant_result = await db.execute(
            select(Task.quadrant, func.count(Task.id).label("count"))
            .group_by(Task.quadrant)
        )
    else:
        # Пользователь видит только свои задачи
        total_result = await db.execute(
            select(func.count(Task.id))
            .where(Task.user_id == current_user.id)
        )
        total_tasks = total_result.scalar() or 0

        quadrant_result = await db.execute(
            select(Task.quadrant, func.count(Task.id).label("count"))
            .where(Task.user_id == current_user.id)
            .group_by(Task.quadrant)
        )

    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for row in quadrant_result.all():
        if row.quadrant in ["Q1", "Q2", "Q3", "Q4"]:
            by_quadrant[row.quadrant] = row.count

    # Статистика по статусу
    if current_user.role.value == "admin":
        status_result = await db.execute(
            select(
                func.count(case((Task.completed == True, 1))).label("completed"),
                func.count(case((Task.completed == False, 1))).label("pending")
            )
        )
    else:
        status_result = await db.execute(
            select(
                func.count(case((Task.completed == True, 1))).label("completed"),
                func.count(case((Task.completed == False, 1))).label("pending")
            ).where(Task.user_id == current_user.id)
        )
    
    status_row = status_result.one()
    by_status = {
        "completed": status_row.completed,
        "pending": status_row.pending
    }

    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status,
        "user_id": current_user.id
    }

# ---------------- GET СТАТИСТИКА ПО ДЕДЛАЙНАМ (с учетом прав) ----------------
@router.get("/deadlines", response_model=List[dict])
async def get_deadline_stats(
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user = Depends(get_current_user)
) -> List[dict]:
    # Админ видит все задачи, пользователь - только свои
    if current_user.role.value == "admin":
        result = await db.execute(
            select(Task).where(
                Task.deadline_at.isnot(None),
                Task.completed.is_(False)
            )
        )
    else:
        result = await db.execute(
            select(Task).where(
                Task.user_id == current_user.id,
                Task.deadline_at.isnot(None),
                Task.completed.is_(False)
            )
        )
    
    tasks = result.scalars().all()
    now = datetime.utcnow()
    response = []

    for task in tasks:
        if task.deadline_at:
            delta = task.deadline_at - now
            days_until_deadline = delta.days
            status = "срочно" if days_until_deadline <= 3 else "не срочно"
            
            response.append({
                "id": task.id,
                "title": task.title,
                "deadline_at": task.deadline_at.isoformat() if task.deadline_at else None,
                "days_until_deadline": days_until_deadline,
                "status": status,
                "user_id": task.user_id
            })

    return response