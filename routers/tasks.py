# routers/tasks.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database import get_db
from schemas import TaskCreate, TaskUpdate, TaskResponse
from crud import TaskCRUD
from utils import calculate_urgency, calculate_days_until_deadline

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

# ===== HELPER: конвертация Task -> TaskResponse =====
def to_response(task) -> TaskResponse:
    days_left = calculate_days_until_deadline(task.deadline_at)
    is_urgent = calculate_urgency(task.deadline_at)
    overdue = days_left is not None and days_left < 0

    quadrant_map_reverse = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}
    quadrant_str = quadrant_map_reverse.get(task.quadrant, "Q4")

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        deadline_at=task.deadline_at,
        quadrant=quadrant_str,
        completed=task.completed,
        created_at=task.created_at,
        completed_at=task.completed_at,
        days_until_deadline=days_left,
        is_urgent=is_urgent,
        overdue=overdue
    )

# ---------------- SEARCH ----------------
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
        "tasks": [to_response(task) for task in tasks]
    }

# ---------------- POST ----------------
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = await TaskCRUD.create(db, task)
    return to_response(db_task)

# ---------------- PUT ----------------
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_db)):
    db_task = await TaskCRUD.update(db, task_id, task_update)
    if not db_task:
        raise HTTPException(404, f"Задача {task_id} не найдена")
    return to_response(db_task)

# ---------------- PATCH ----------------
@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    db_task = await TaskCRUD.complete(db, task_id)
    if not db_task:
        raise HTTPException(404, f"Задача {task_id} не найдена")
    return to_response(db_task)

# ---------------- DELETE ----------------
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    db_task = await TaskCRUD.delete(db, task_id)
    if not db_task:
        raise HTTPException(404, f"Задача {task_id} не найдена")
    return None

# ---------------- GET ALL ----------------
@router.get("/", response_model=dict)
async def get_all_tasks(db: AsyncSession = Depends(get_db)):
    tasks = await TaskCRUD.get_all(db)
    return {
        "count": len(tasks),
        "tasks": [to_response(t) for t in tasks]
    }

# ---------------- GET BY ID ----------------
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await TaskCRUD.get_by_id(db, task_id)
    if not task:
        raise HTTPException(404, f"Задача {task_id} не найдена")
    return to_response(task)

# ---------------- STATUS ----------------
@router.get("/status/{status}", response_model=List[TaskResponse])
async def get_tasks_by_status(status: str, db: AsyncSession = Depends(get_db)):
    if status not in ["completed", "pending"]:
        raise HTTPException(400, "Используйте: 'completed' или 'pending'")
    completed = status == "completed"
    tasks = await TaskCRUD.get_by_status(db, completed)
    return [to_response(t) for t in tasks]

# ---------------- QUADRANT ----------------
@router.get("/quadrant/{quadrant}", response_model=dict)
async def get_tasks_by_quadrant(quadrant: str, db: AsyncSession = Depends(get_db)):
    quadrant_map = {"Q1": "Q1", "Q2": "Q2", "Q3": "Q3", "Q4": "Q4"}
    if quadrant not in quadrant_map:
        raise HTTPException(status_code=400, detail="Используйте: Q1, Q2, Q3, Q4")
    
    tasks = await TaskCRUD.get_by_quadrant(db, quadrant)
    
    return {
        "quadrant": quadrant,
        "count": len(tasks),
        "tasks": [to_response(t) for t in tasks]
    }
