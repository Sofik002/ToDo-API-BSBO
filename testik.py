# check_env.py
import os
from dotenv import load_dotenv

load_dotenv()

print("Текущая рабочая директория:", os.getcwd())
print("Файл .env существует:", os.path.exists('.env'))

url = os.getenv("DATABASE_URL")
print("\nDATABASE_URL:", url)
if url:
    print("Начинается с 'postgresql+asyncpg://':", url.startswith('postgresql+asyncpg://'))
    print("Длина URL:", len(url))