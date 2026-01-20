import asyncpg
import asyncio
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def parse_database_url(database_url):
    if not database_url:
        return None
    
    parsed = urlparse(database_url)
    
    scheme = parsed.scheme.replace('+asyncpg', '')
    
    return {
        'user': parsed.username or 'postgres',
        'password': parsed.password or '',
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/') or 'postgres'
    }

async def test_with_password():
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL не найден в .env")
        return
    
    print(f"🔗 URL из .env: {database_url}")
    
    params = parse_database_url(database_url)
    
    if not params:
        print("❌ Не удалось распарсить DATABASE_URL")
        return
    
    print(f"📋 Параметры подключения: {params}")
    
    try:
        conn = await asyncpg.connect(
            user=params['user'],
            password=params['password'],
            host=params['host'],
            port=params['port'],
            database=params['database']
        )
        
        print("✅ Успешное подключение через asyncpg!")
        
        db_name = await conn.fetchval("SELECT current_database()")
        print(f"📊 Текущая база: {db_name}")
        
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        print(f"📋 Найдено таблиц: {len(tables)}")
        
        for table in tables:
            print(f"   • {table['table_name']}")
        
        await conn.close()
        return True
        
    except asyncpg.InvalidPasswordError:
        print("❌ Неправильный пароль!")
        return False
    except asyncpg.ConnectionFailureError as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_with_password())
    if success:
        print("\n🎉 Всё работает! Можешь запускать приложение.")
    else:
        print("\n💡 Проверь пароль и настройки в .env")