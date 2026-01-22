# create_test_tasks.py
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from database import async_session_maker
from models.user import User, UserRole
from models.task import Task
from utils import determine_quadrant, calculate_urgency

async def create_test_tasks():
    """Создаем тестовые задачи для пользователя"""
    async with async_session_maker() as session:
        print("📝 Создаем тестовые задачи...")
        
        # Находим пользователя
        result = await session.execute(
            select(User).where(User.email.like("%@example.com"))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Не найден пользователь с email @example.com")
            print("   Сначала зарегистрируйтесь через API")
            return
        
        print(f"✅ Найден пользователь: {user.nickname} (id: {user.id})")
        
        # Создаем тестовые задачи
        test_tasks = [
            {
                "title": "Срочная и важная задача",
                "description": "Сделать срочный отчет",
                "is_important": True,
                "deadline_at": datetime.utcnow() + timedelta(days=1),  # Завтра
                "completed": False
            },
            {
                "title": "Важная, но не срочная",
                "description": "Изучить новую технологию",
                "is_important": True,
                "deadline_at": datetime.utcnow() + timedelta(days=10),
                "completed": False
            },
            {
                "title": "Срочная, но не важная",
                "description": "Ответить на письма",
                "is_important": False,
                "deadline_at": datetime.utcnow() + timedelta(days=2),
                "completed": False
            },
            {
                "title": "Не срочная и не важная",
                "description": "Посмотреть YouTube",
                "is_important": False,
                "deadline_at": datetime.utcnow() + timedelta(days=30),
                "completed": False
            },
            {
                "title": "Завершенная задача",
                "description": "Купить продукты",
                "is_important": True,
                "deadline_at": datetime.utcnow() - timedelta(days=1),  # Вчера
                "completed": True
            }
        ]
        
        created_count = 0
        for task_data in test_tasks:
            # Определяем квадрант
            is_urgent = calculate_urgency(task_data["deadline_at"])
            quadrant = determine_quadrant(task_data["is_important"], is_urgent)
            
            # Создаем задачу
            task = Task(
                title=task_data["title"],
                description=task_data["description"],
                is_important=task_data["is_important"],
                deadline_at=task_data["deadline_at"],
                quadrant=quadrant,
                completed=task_data["completed"],
                user_id=user.id,
                completed_at=datetime.utcnow() if task_data["completed"] else None
            )
            
            session.add(task)
            created_count += 1
        
        await session.commit()
        print(f"✅ Создано {created_count} тестовых задач")
        
        # Показываем статистику
        result = await session.execute(
            select(Task).where(Task.user_id == user.id)
        )
        all_tasks = result.scalars().all()
        
        print(f"\n📊 Статистика для пользователя {user.nickname}:")
        print(f"   Всего задач: {len(all_tasks)}")
        
        # Группируем по квадрантам
        quadrants = {}
        for task in all_tasks:
            quadrants[task.quadrant] = quadrants.get(task.quadrant, 0) + 1
        
        for q in ["Q1", "Q2", "Q3", "Q4"]:
            count = quadrants.get(q, 0)
            print(f"   {q}: {count} задач")
        
        completed_count = sum(1 for t in all_tasks if t.completed)
        print(f"   Завершено: {completed_count}")
        print(f"   В работе: {len(all_tasks) - completed_count}")

if __name__ == "__main__":
    asyncio.run(create_test_tasks())