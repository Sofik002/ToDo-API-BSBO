import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL не найден в переменных окружения."
    )

print(f"Подключение к базе данных: {DATABASE_URL}")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    try:
        from models.task import Task
        
        print("Проверяем структуру таблиц...")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        print("Структура таблиц проверена!")
        
    except Exception as e:
        print(f"Ошибка при проверке таблиц: {e}")
        raise

async def health_check() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return False