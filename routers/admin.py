# routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_async_session  # ИСПРАВЛЕН ИМПОРТ
from models.user import User, UserRole
from models.task import Task
from dependencies import get_current_admin
from typing import List

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/users", response_model=List[dict])
async def get_all_users_with_task_count(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_session)  # ИСПРАВЛЕНО
):
    """Получить всех пользователей с количеством их задач"""
    result = await db.execute(
        select(
            User.id,
            User.nickname,
            User.email,
            User.role,
            func.count(Task.id).label("task_count")
        ).outerjoin(Task, User.id == Task.user_id)
        .group_by(User.id)
    )
    
    users_with_counts = result.all()
    
    return [
        {
            "id": user.id,
            "nickname": user.nickname,
            "email": user.email,
            "role": user.role.value,
            "task_count": user.task_count or 0
        }
        for user in users_with_counts
    ]