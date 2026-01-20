# routers/tasks.py
from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from schemas import TaskCreate, TaskUpdate, TaskResponse
from database import get_db
from crud import TaskCRUD

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}}
)

@router.get("/")
async def get_all_tasks(
    db: AsyncSession = Depends(get_db)
) -> dict:
    tasks = await TaskCRUD.get_all(db)
    return {
        "count": len(tasks),
        "tasks": [task.to_dict() for task in tasks]
    }

@router.get("/search")
async def search_tasks(
    q: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="Поисковый запрос должен содержать минимум 2 символа"
        )
    
    tasks = await TaskCRUD.search(db, q)
    
    if not tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Задачи по запросу '{q}' не найдены"
        )
    
    return {
        "query": q,
        "count": len(tasks),
        "tasks": [task.to_dict() for task in tasks]
    }

@router.get("/status/{status}")
async def get_tasks_by_status(
    status: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный статус. Используйте: 'completed' или 'pending'"
        )
    
    completed = (status == "completed")
    tasks = await TaskCRUD.get_by_status(db, completed)
    
    if not tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Задачи со статусом '{status}' не найдены"
        )
    
    return {
        "status": status,
        "count": len(tasks),
        "tasks": [task.to_dict() for task in tasks]
    }

@router.get("/quadrant/{quadrant}")
async def get_tasks_by_quadrant(
    quadrant: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"
        )
    
    tasks = await TaskCRUD.get_by_quadrant(db, quadrant)
    
    if not tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Задачи в квадранте '{quadrant}' не найдены"
        )
    
    return {
        "quadrant": quadrant,
        "count": len(tasks),
        "tasks": [task.to_dict() for task in tasks]
    }

@router.get("/{task_id}")
async def get_task_by_id(
    task_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    task = await TaskCRUD.get_by_id(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Задача с ID {task_id} не найдена"
        )
    
    return task.to_dict()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    db_task = await TaskCRUD.create(db, task)
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    db_task = await TaskCRUD.update(db, task_id, task_update)
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return db_task

@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    db_task = await TaskCRUD.complete(db, task_id)
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return db_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_task = await TaskCRUD.delete(db, task_id)
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)