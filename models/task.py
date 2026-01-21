# models/task.py
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    is_important = Column(Boolean, default=False)
    deadline_at = Column(DateTime, nullable=True)
    quadrant = Column(String(2), nullable=False)  # Оставляем String!
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # ===== helpers =====
    def days_until_deadline(self) -> int | None:
        if not self.deadline_at:
            return None
        today = datetime.utcnow().date()
        deadline_date = self.deadline_at.date()
        return (deadline_date - today).days
