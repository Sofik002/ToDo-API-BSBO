# models/__init__.py
from .task import Task

# Экспортируем Base из database чтобы он был доступен в Task
from database import Base

__all__ = ["Task", "Base"]