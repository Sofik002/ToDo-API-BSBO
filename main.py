# Главный файл приложения
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact = {"name": "София"}
)

# Временное хранилище (позже будет заменено на PostgreSQL)
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": None,
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now()
    },
]

@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Привет, студент!",
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "contact": app.contact
    }

@app.get("/tasks") 
async def get_all_tasks() -> dict: 
    return { 
        "count": len(tasks_db),  # считает количество записей в хранилище 
        "tasks": tasks_db # выводит всё, что есть в хранилище 
    }

# 2) Endpoint для получения статистики по задачам (ДОЛЖЕН БЫТЬ ПЕРЕД /tasks/{task_id})
@app.get("/tasks/stats")
async def get_tasks_stats() -> dict:
    """Получить статистику по всем задачам"""
    total_tasks = len(tasks_db)
    
    # Статистика по квадрантам
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    # Статистика по статусу выполнения
    by_status = {"completed": 0, "pending": 0}
    
    for task in tasks_db:
        # Считаем задачи по квадрантам
        quadrant = task.get("quadrant")
        if quadrant in by_quadrant:
            by_quadrant[quadrant] += 1
        
        # Считаем задачи по статусу
        if task.get("completed"):
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1
    
    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }

# 4) Endpoint для поиска задач по ключевому слову (ДОЛЖЕН БЫТЬ ПЕРЕД /tasks/{task_id})
@app.get("/tasks/search")
async def search_tasks(q: str) -> dict:
    """Поиск задач по ключевому слову в названии или описании"""
    
    # Проверка минимальной длины запроса
    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="Поисковый запрос должен содержать минимум 2 символа"
        )
    
    q_lower = q.lower()
    found_tasks = []
    
    for task in tasks_db:
        # Проверяем название
        title = task.get("title", "").lower()
        # Проверяем описание (может быть None)
        description = task.get("description", "").lower() if task.get("description") else ""
        
        if q_lower in title or q_lower in description:
            found_tasks.append(task)
    
    # Проверка, найдены ли задачи
    if not found_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Задачи по запросу '{q}' не найдены"
        )
    
    return {
        "query": q,
        "count": len(found_tasks),
        "tasks": found_tasks
    }

# 3) Endpoint для фильтрации задач по статусу выполнения
@app.get("/tasks/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    """Получить задачи по статусу выполнения"""
    
    # Проверка валидности статуса
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный статус. Используйте: 'completed' или 'pending'"
        )
    
    # Преобразуем статус в булево значение
    target_completed = (status == "completed")
    
    # Фильтрация задач
    filtered_tasks = [
        task
        for task in tasks_db
        if task.get("completed") == target_completed
    ]
    
    # Проверка, найдены ли задачи
    if not filtered_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Задачи со статусом '{status}' не найдены"
        )
    
    return {
        "status": status,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

@app.get("/tasks/quadrant/{quadrant}") 
async def get_tasks_by_quadrant(quadrant: str) -> dict: 
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]: 
        raise HTTPException(
            status_code=400, 
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4" 
        ) 
    
    filtered_tasks = [ 
        task 
        for task in tasks_db 
        if task.get("quadrant") == quadrant 
    ]
    
    # Проверка, найдены ли задачи
    if not filtered_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Задачи в квадранте '{quadrant}' не найдены"
        )
    
    return { 
        "quadrant": quadrant, 
        "count": len(filtered_tasks), 
        "tasks": filtered_tasks 
    }

# 1) Endpoint для получения задачи по ID (ДОЛЖЕН БЫТЬ ПОСЛЕ ВСЕХ КОНКРЕТНЫХ ПУТЕЙ)
@app.get("/tasks/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    """Получить задачу по ID"""
    
    # Ищем задачу по ID
    for task in tasks_db:
        if task.get("id") == task_id:
            return task
    
    # Если задача не найдена
    raise HTTPException(
        status_code=404,
        detail=f"Задача с ID {task_id} не найдена"
    )