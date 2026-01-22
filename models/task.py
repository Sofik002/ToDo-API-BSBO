# models/task.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)  # Теперь TEXT
    is_important = Column(Boolean, default=False, nullable=False)
    deadline_at = Column(DateTime, nullable=True)
    quadrant = Column(String(2), default="Q4", nullable=False)
    completed = Column(Boolean, default=False, nullable=False)  # Было is_completed
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Связь с пользователем
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Связь
    owner = relationship("User", back_populates="tasks")
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', quadrant='{self.quadrant}')>"
    
    # ===== helpers =====
    def days_until_deadline(self) -> int | None:
        if not self.deadline_at:
            return None
        today = datetime.utcnow().date()
        deadline_date = self.deadline_at.date()
        return (deadline_date - today).days