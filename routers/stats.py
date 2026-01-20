# routers/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models.task import Task

router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)

@router.get("/")
async def get_tasks_stats(db: AsyncSession = Depends(get_db)) -> dict:
    # Общее количество задач
    total_result = await db.execute(select(func.count(Task.id)))
    total_tasks = total_result.scalar() or 0
    
    # Статистика по квадрантам
    quadrant_result = await db.execute(
        select(Task.quadrant, func.count(Task.id))
        .group_by(Task.quadrant)
    )
    
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for quadrant, count in quadrant_result.all():
        if quadrant in by_quadrant:
            by_quadrant[quadrant] = count
    
    # Статистика по статусам
    completed_result = await db.execute(
        select(func.count(Task.id))
        .where(Task.completed == True)
    )
    completed_count = completed_result.scalar() or 0
    
    pending_count = total_tasks - completed_count
    
    by_status = {
        "completed": completed_count,
        "pending": pending_count
    }
    
    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }