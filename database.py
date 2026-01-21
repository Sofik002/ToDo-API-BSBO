# database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

# Загружаем .env
load_dotenv()

# Подключение к PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/todo_db"
)

# Async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# Async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base для моделей
Base = declarative_base()

# Dependency для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Инициализация базы данных
async def init_db():
    from models.task import Task  # Импорт модели внутри функции
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База данных инициализирована")
