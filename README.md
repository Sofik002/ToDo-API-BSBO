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
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

#4. Установить зависимости
pip install -r requirements.txt

#5. Запустить сервер
uvicorn main:app --reload
```
## Настройка базы данных PostgreSQL

### 1. Установка и запуск PostgreSQL

- Скачать с [официального сайта](https://www.postgresql.org/download/windows/)
- Установить, запомнив пароль для пользователя `postgres`
- Служба запустится автоматически

## Создание базы данных и таблицы

### Подключись к PostgreSQL и выполни:

```bash
-- Создание базы данных
CREATE DATABASE todo_db;

-- Подключение к созданной базе
\c todo_db

-- Создание таблицы tasks
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    description TEXT,
    is_important BOOLEAN DEFAULT FALSE,
    is_urgent BOOLEAN DEFAULT FALSE,
    quadrant VARCHAR(2) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Заполнение таблицы тестовыми данными
INSERT INTO tasks (title, description, is_important, is_urgent, quadrant, completed) VALUES
('Подготовить отчет по практике', 'Собрать все материалы и оформить отчет по FastAPI проекту', TRUE, TRUE, 'Q1', FALSE),
('Изучить PostgreSQL', 'Освоить работу с базами данных PostgreSQL для данного проекта', TRUE, FALSE, 'Q2', FALSE),
('Сходить на валберис', 'Забрать все покупки из двух пунктов выдачи', FALSE, TRUE, 'Q3', FALSE),
('Посидеть в тик токе', 'Поскидывать видосы друзьям', FALSE, FALSE, 'Q4', TRUE),
('Сдать проект по FastAPI', 'Завершить разработку API и написать документацию', TRUE, TRUE, 'Q1', FALSE),
('Изучить SQLAlchemy', 'Прочитать документацию и попробовать примеры', TRUE, FALSE, 'Q2', FALSE),
('Сходить на лекцию', NULL, FALSE, TRUE, 'Q3', FALSE),
('Посмотреть сериал', 'Новый сезон любимого сериала', FALSE, FALSE, 'Q4', TRUE);
```
## Доступ к API
- **Документация Swagger UI:** -  http://localhost:8000/docs
- **Все задачи:** - http://localhost:8000/api/v1/tasks
- **Статистика по квадрантам** - http://localhost:8000/api/v1/stats