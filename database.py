# database.py - Правильная версия (без дублирования URL)
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

# Загружаем переменные окружения из .env файла
load_dotenv()

# ТОЛЬКО получение переменной из .env, без значения по умолчанию
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверяем, что переменная загрузилась
if not DATABASE_URL:
    raise ValueError(
        "❌ DATABASE_URL не найден в переменных окружения.\n"
        "Добавьте в .env файл:\n"
        "DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todo_db"
    )

print(f"🔗 Подключение к базе данных: {DATABASE_URL}")

# Создаем асинхронный движок SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
    pool_pre_ping=True,
)

# Фабрика для создания асинхронных сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии БД.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """
    Проверка и создание таблиц если их нет.
    """
    try:
        from models.task import Task
        
        print("🔍 Проверяем структуру таблиц...")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        print("✅ Структура таблиц проверена!")
        
    except Exception as e:
        print(f"⚠️ Ошибка при проверке таблиц: {e}")
        raise

async def health_check() -> bool:
    """
    Проверка подключения к БД.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False