# routers/tasks.py
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime

from database import get_async_session  # ИСПРАВЛЕН ИМПОРТ
from schemas import TaskCreate, TaskUpdate, TaskResponse
from models.task import Task
from models.user import User
from dependencies import get_current_user
from utils import calculate_urgency, calculate_days_until_deadline, determine_quadrant

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

# ===== HELPER: конвертация Task -> TaskResponse =====
def to_response(task) -> TaskResponse:
    days_left = calculate_days_until_deadline(task.deadline_at)
    is_urgent = calculate_urgency(task.deadline_at)
    overdue = days_left is not None and days_left < 0

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        deadline_at=task.deadline_at,
        quadrant=task.quadrant,
        completed=task.completed,
        created_at=task.created_at,
        completed_at=task.completed_at,
        days_until_deadline=days_left,
        is_urgent=is_urgent,
        overdue=overdue
    )
    
@router.get("/today", response_model=dict)
async def get_tasks_due_today(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    today = datetime.utcnow().date()
    
    # Админ видит все задачи, пользователь - только свои
    if current_user.role.value == "admin":
        result = await db.execute(
            select(Task).where(
                Task.deadline_at.isnot(None),
                Task.completed == False
            )
        )
    else:
        result = await db.execute(
            select(Task).where(
                Task.user_id == current_user.id,
                Task.deadline_at.isnot(None),
                Task.completed == False
            )
        )
    
    all_tasks = result.scalars().all()
    
    # Фильтруем на сегодня в коде Python
    today_tasks = []
    for task in all_tasks:
        if task.deadline_at and task.deadline_at.date() == today:
            today_tasks.append(task)
    
    return {
        "date": today.isoformat(),
        "count": len(today_tasks),
        "tasks": [to_response(t) for t in today_tasks]
    }

@router.get("/search", response_model=dict)
async def search_tasks(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user: User = Depends(get_current_user)
):
    # Админ ищет во всех задачах, пользователь - только в своих
    if current_user.role.value == "admin":
        result = await db.execute(
            select(Task).where(
                (Task.title.ilike(f"%{q}%")) |
                (Task.description.ilike(f"%{q}%"))
            )
        )
    else:
        result = await db.execute(
            select(Task).where(
                Task.user_id == current_user.id,
                ((Task.title.ilike(f"%{q}%")) |
                 (Task.description.ilike(f"%{q}%")))
            )
        )
    
    tasks = result.scalars().all()
    
    if not tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Задачи по запросу '{q}' не найдены"
        )
    
    return {
        "query": q,
        "count": len(tasks),
        "tasks": [to_response(task) for task in tasks]
    }

# ---------------- CREATE ---------------- 
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user: User = Depends(get_current_user)
):
    # Автоматически определяем квадрант
    is_urgent = calculate_urgency(task.deadline_at)
    quadrant_str = determine_quadrant(task.is_important, is_urgent)
    
    db_task = Task(
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        deadline_at=task.deadline_at,
        quadrant=quadrant_str,
        completed=False,
        user_id=current_user.id  # Привязываем к текущему пользователю
    )
    
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return to_response(db_task)

# ---------------- GET ALL (с учетом прав) ----------------
@router.get("/", response_model=dict)
async def get_all_tasks(
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user: User = Depends(get_current_user)
):
    # Админ видит все задачи, пользователь - только свои
    if current_user.role.value == "admin":
        result = await db.execute(select(Task))
    else:
        result = await db.execute(
            select(Task).where(Task.user_id == current_user.id)
        )
    
    tasks = result.scalars().all()
    return {
        "count": len(tasks),
        "tasks": [to_response(t) for t in tasks]
    }


# ---------------- UPDATE (с учетом прав) ----------------
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(404, f"Задача {task_id} не найдена")
    
    # Проверяем права доступа
    if current_user.role.value != "admin" and task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этой задаче"
        )
    
    # Обновляем поля
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(task, field, value)
    
    # Пересчитываем квадрант
    is_urgent = calculate_urgency(task.deadline_at)
    task.quadrant = determine_quadrant(task.is_important, is_urgent)
    
    await db.commit()
    await db.refresh(task)
    return to_response(task)

# ---------------- COMPLETE (с учетом прав) ----------------
@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(404, f"Задача {task_id} не найдена")
    
    # Проверяем права доступа
    if current_user.role.value != "admin" and task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этой задаче"
        )
    
    task.completed = True
    task.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(task)
    return to_response(task)

# ---------------- DELETE (с учетом прав) ----------------
@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(404, f"Задача {task_id} не найдена")
    
    # Проверяем права доступа
    if current_user.role.value != "admin" and task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этой задаче"
        )
    
    await db.delete(task)
    await db.commit()
    
    return {
        "message": "Задача успешно удалена",
        "id": task_id,
        "title": task.title
    }


# ---------------- GET BY STATUS (с учетом прав) ----------------
@router.get("/status/{status}", response_model=List[TaskResponse])
async def get_tasks_by_status(
    status: str,
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user: User = Depends(get_current_user)
):
    if status not in ["completed", "pending"]:
        raise HTTPException(400, "Используйте: 'completed' или 'pending'")
    
    completed = status == "completed"
    
    # Админ видит все задачи, пользователь - только свои
    if current_user.role.value == "admin":
        result = await db.execute(
            select(Task).where(Task.completed == completed)
        )
    else:
        result = await db.execute(
            select(Task).where(
                Task.user_id == current_user.id,
                Task.completed == completed
            )
        )
    
    tasks = result.scalars().all()
    return [to_response(t) for t in tasks]

# ---------------- GET BY QUADRANT (с учетом прав) ----------------
@router.get("/quadrant/{quadrant}", response_model=dict)
async def get_tasks_by_quadrant(
    quadrant: str,
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user: User = Depends(get_current_user)
):
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(status_code=400, detail="Используйте: Q1, Q2, Q3, Q4")
    
    # Админ видит все задачи, пользователь - только свои
    if current_user.role.value == "admin":
        result = await db.execute(
            select(Task).where(Task.quadrant == quadrant)
        )
    else:
        result = await db.execute(
            select(Task).where(
                Task.user_id == current_user.id,
                Task.quadrant == quadrant
            )
        )
    
    tasks = result.scalars().all()
    
    return {
        "quadrant": quadrant,
        "count": len(tasks),
        "tasks": [to_response(t) for t in tasks]
    }

# ---------------- GET BY ID (с учетом прав) ----------------
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: int,
    db: AsyncSession = Depends(get_async_session),  # ИСПРАВЛЕНО
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(404, f"Задача {task_id} не найдена")
    
    # Проверяем права доступа
    if current_user.role.value != "admin" and task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этой задаче"
        )
    
    return to_response(task)