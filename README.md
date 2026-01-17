# ToDo лист API

**API для управления задачами с использованием матрицы Эйзенхауэра.**

## Технологии
- **Python 3.11+**
- **FastAPI** - веб-фреймворк для API
- **Uvicorn** - сервер для запуска

## Автор
**София Волвенко**

## Запуск проекта

```bash
#1. Клонировать репозиторий
git clone https://github.com/ваш-аккаунт/ToDo-API-BSBO.git
cd ToDo-API-BSBO

#2. Создать виртуальное окружение
python -m venv venv

#3. Активировать окружение
#Windows:
venv\Scripts\activate
#Linux/Mac:
source venv/bin/activate

#4. Установить зависимости
pip install -r requirements.txt

#5. Запустить сервер
uvicorn main:app --reload

