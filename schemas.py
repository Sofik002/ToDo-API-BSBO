# schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# Базовая схема для Task
class TaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Название задачи"
    )
    
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Описание задачи"
    )
    
    is_important: bool = Field(
        False,
        description="Важность задачи"
    )
    
    is_urgent: bool = Field(
        False,
        description="Срочность задачи"
    )
    
    quadrant: str = Field(
        ...,
        description="Квадрант матрицы Эйзенхауэра (Q1, Q2, Q3, Q4)",
        examples=["Q1", "Q2", "Q3", "Q4"]
    )
    
    completed: bool = Field(
        False,
        description="Статус выполнения задачи"
    )
    
    @field_validator('quadrant')
    @classmethod
    def validate_quadrant(cls, v: str) -> str:
        """Валидация квадранта"""
        if v not in ['Q1', 'Q2', 'Q3', 'Q4']:
            raise ValueError('Квадрант должен быть Q1, Q2, Q3 или Q4')
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Валидация заголовка"""
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Название задачи должно быть не менее 3 символов')
        return v

# Схема для создания новой задачи
class TaskCreate(TaskBase):
    pass

# Схема для обновления задачи
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Новое название задачи"
    )
    
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Новое описание"
    )
    
    is_important: Optional[bool] = Field(
        None,
        description="Новая важность"
    )
    
    is_urgent: Optional[bool] = Field(
        None,
        description="Новая срочность"
    )
    
    quadrant: Optional[str] = Field(
        None,
        description="Новый квадрант"
    )
    
    completed: Optional[bool] = Field(
        None,
        description="Статус выполнения"
    )
    
    @field_validator('quadrant')
    @classmethod
    def validate_quadrant(cls, v: Optional[str]) -> Optional[str]:
        """Валидация квадранта для обновления"""
        if v is not None and v not in ['Q1', 'Q2', 'Q3', 'Q4']:
            raise ValueError('Квадрант должен быть Q1, Q2, Q3 или Q4')
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Валидация заголовка для обновления"""
        if v is not None:
            v = v.strip()
            if len(v) < 3:
                raise ValueError('Название задачи должно быть не менее 3 символов')
        return v

# Модель для ответа
class TaskResponse(TaskBase):
    id: int = Field(
        ...,
        description="Уникальный идентификатор задачи",
        examples=[1]
    )
    
    created_at: datetime = Field(
        ...,
        description="Дата и время создания задачи"
    )
    
    completed_at: Optional[datetime] = Field(
        None,
        description="Дата и время выполнения задачи"
    )
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }