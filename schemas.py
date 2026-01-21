from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ------------------ Схема для создания ------------------
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_important: bool = False
    deadline_at: Optional[datetime] = None

# ------------------ Схема для обновления ------------------
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_important: Optional[bool] = None
    deadline_at: Optional[datetime] = None
    completed: Optional[bool] = None

# ------------------ Схема для ответа ------------------
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    is_important: bool = False
    deadline_at: Optional[datetime] = None
    quadrant: str
    completed: bool = False
    created_at: datetime
    completed_at: Optional[datetime] = None
    days_until_deadline: Optional[int] = None
    is_urgent: bool = False
    overdue: bool = False

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# ------------------ Схема для статистики по дедлайнам ------------------
class TimingStatsResponse(BaseModel):
    completed_on_time: int = Field(..., description="Количество задач, завершенных в срок")
    completed_late: int = Field(..., description="Количество задач, завершенных с нарушением сроков")
    on_plan_pending: int = Field(..., description="Количество задач в работе, выполняемых в соответствии с планом")
    overdue_pending: int = Field(..., description="Количество просроченных незавершенных задач")