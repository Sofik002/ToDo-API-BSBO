from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.task import Task
from schemas import TaskCreate, TaskUpdate
from datetime import datetime

class TaskCRUD:
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Task).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, task_id: int):
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, task: TaskCreate):
        if task.is_important and task.is_urgent:
            quadrant = "Q1"
        elif task.is_important and not task.is_urgent:
            quadrant = "Q2"
        elif not task.is_important and task.is_urgent:
            quadrant = "Q3"
        else:
            quadrant = "Q4"
        
        db_task = Task(
            title=task.title,
            description=task.description,
            is_important=task.is_important,
            is_urgent=task.is_urgent,
            quadrant=quadrant,
            completed=False
        )
        
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task
    
    @staticmethod
    async def update(db: AsyncSession, task_id: int, task_update: TaskUpdate):
        db_task = await TaskCRUD.get_by_id(db, task_id)
        if not db_task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True, exclude={"id"})
        
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        if "is_important" in update_data or "is_urgent" in update_data:
            if db_task.is_important and db_task.is_urgent:
                db_task.quadrant = "Q1"
            elif db_task.is_important and not db_task.is_urgent:
                db_task.quadrant = "Q2"
            elif not db_task.is_important and db_task.is_urgent:
                db_task.quadrant = "Q3"
            else:
                db_task.quadrant = "Q4"
        
        await db.commit()
        await db.refresh(db_task)
        return db_task
    
    @staticmethod
    async def delete(db: AsyncSession, task_id: int):
        db_task = await TaskCRUD.get_by_id(db, task_id)
        if db_task:
            await db.delete(db_task)
            await db.commit()
        return db_task
    
    @staticmethod
    async def complete(db: AsyncSession, task_id: int):
        db_task = await TaskCRUD.get_by_id(db, task_id)
        if db_task:
            db_task.completed = True
            db_task.completed_at = datetime.now()
            await db.commit()
            await db.refresh(db_task)
        return db_task
    
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
    
    @staticmethod
    async def get_by_status(db: AsyncSession, completed: bool):
        result = await db.execute(
            select(Task).where(Task.completed == completed)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_by_quadrant(db: AsyncSession, quadrant: str):
        result = await db.execute(
            select(Task).where(Task.quadrant == quadrant)
        )
        return result.scalars().all()