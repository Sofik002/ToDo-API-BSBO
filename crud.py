# crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models.task import Task
from schemas import TaskCreate, TaskUpdate
from utils import calculate_urgency, determine_quadrant
from datetime import datetime
from typing import Optional, List

class TaskCRUD:

    @staticmethod
    async def create(db: AsyncSession, task_create: TaskCreate) -> Task:
        deadline = task_create.deadline_at
        if deadline:
            deadline = deadline.replace(tzinfo=None)

        is_urgent = calculate_urgency(deadline)
        
        # Вычисляем квадрант как строку
        quadrant_str = determine_quadrant(task_create.is_important, is_urgent)
        # НЕ конвертируем в число!
        
        db_task = Task(
            title=task_create.title,
            description=task_create.description,
            is_important=task_create.is_important,
            deadline_at=deadline,
            quadrant=quadrant_str,  # Сохраняем как строку "Q1"
            completed=False
        )
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task

    @staticmethod
    async def update(db: AsyncSession, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        task = await db.get(Task, task_id)
        if not task:
            return None

        # Применяем все переданные поля
        update_data = task_update.dict(exclude_unset=True, exclude={"quadrant"})
        for field, value in update_data.items():
            setattr(task, field, value)

        # Пересчитываем urgent и quadrant после обновления
        is_urgent = calculate_urgency(task.deadline_at)
        task.quadrant = determine_quadrant(task.is_important, is_urgent)

        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def complete(db: AsyncSession, task_id: int) -> Optional[Task]:
        task = await db.get(Task, task_id)
        if not task:
            return None
        task.completed = True
        task.completed_at = datetime.utcnow()

        # Пересчитываем квадрант (как строку!)
        is_urgent = calculate_urgency(task.deadline_at)
        quadrant_str = determine_quadrant(task.is_important, is_urgent)
        task.quadrant = quadrant_str  # Сохраняем строку
        
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def delete(db: AsyncSession, task_id: int) -> Optional[Task]:
        task = await db.get(Task, task_id)
        if not task:
            return None
        await db.delete(task)
        await db.commit()
        return task

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Task]:
        result = await db.execute(select(Task))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, task_id: int) -> Optional[Task]:
        return await db.get(Task, task_id)

    @staticmethod
    async def get_by_status(db: AsyncSession, completed: bool) -> List[Task]:
        result = await db.execute(select(Task).where(Task.completed == completed))
        return result.scalars().all()

    @staticmethod
    async def get_by_quadrant(db: AsyncSession, quadrant: str) -> list:
        """Получить задачи по квадранту Q1..Q4"""
        result = await db.execute(
            select(Task).where(Task.quadrant == quadrant)  # строка, не число!
        )
        tasks = result.scalars().all()
        return tasks

    @staticmethod
    async def search(db: AsyncSession, query: str):
        if len(query) < 2:
            return []
            
        result = await db.execute(
            select(Task).where(
                Task.title.ilike(f"%{query}%") | 
                Task.description.ilike(f"%{query}%")
            )
        )
        return result.scalars().all()
