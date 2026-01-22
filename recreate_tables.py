# migrate_database.py
import asyncio
from sqlalchemy import text
from database import engine

async def migrate_database():
    async with engine.begin() as conn:
        print("🔄 Начинаем миграцию базы данных...")
        
        # 1. Создаем таблицу users
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                nickname VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                role VARCHAR(10) NOT NULL DEFAULT 'user'
            );
        """))
        print("✅ Таблица users создана/проверена")
        
        # 2. Создаем индексы для users
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """))
        print("✅ Индексы для users созданы/проверены")
        
        # 3. Проверяем, существует ли столбец user_id в таблице tasks
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='tasks' AND column_name='user_id';
        """))
        
        column_exists = result.fetchone()
        
        if not column_exists:
            # Добавляем столбец user_id если его нет
            await conn.execute(text("ALTER TABLE tasks ADD COLUMN user_id INTEGER;"))
            print("✅ Столбец user_id добавлен в tasks")
        else:
            print("✅ Столбец user_id уже существует в tasks")
        
        # 4. Проверяем, существует ли внешний ключ
        result = await conn.execute(text("""
            SELECT conname 
            FROM pg_constraint 
            WHERE conrelid = 'tasks'::regclass AND conname = 'fk_tasks_user_id';
        """))
        
        constraint_exists = result.fetchone()
        
        if not constraint_exists:
            # Создаем внешний ключ если его нет
            await conn.execute(text("""
                ALTER TABLE tasks 
                ADD CONSTRAINT fk_tasks_user_id 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
            """))
            print("✅ Внешний ключ fk_tasks_user_id создан")
        else:
            print("✅ Внешний ключ fk_tasks_user_id уже существует")
        
        # 5. Проверяем, существует ли индекс
        result = await conn.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'tasks' AND indexname = 'idx_tasks_user_id';
        """))
        
        index_exists = result.fetchone()
        
        if not index_exists:
            # Создаем индекс если его нет
            await conn.execute(text("""
                CREATE INDEX idx_tasks_user_id ON tasks(user_id);
            """))
            print("✅ Индекс idx_tasks_user_id создан")
        else:
            print("✅ Индекс idx_tasks_user_id уже существует")
        
        print("🎉 База данных успешно обновлена!")

if __name__ == "__main__":
    asyncio.run(migrate_database())