# utils.py
from datetime import datetime
from typing import Optional

def calculate_days_until_deadline(deadline_at: Optional[datetime]) -> Optional[int]:
    """
    Возвращает количество дней до дедлайна.
    Используем naive datetime UTC.
    """
    if not deadline_at:
        return None
    now = datetime.utcnow()
    delta = deadline_at - now
    return delta.days

def calculate_urgency(deadline_at: Optional[datetime]) -> bool:
    """
    Возвращает True, если дедлайн ≤ 3 дней от текущей даты.
    """
    days_left = calculate_days_until_deadline(deadline_at)
    if days_left is None:
        return False
    return days_left <= 3

def determine_quadrant(is_important: bool, is_urgent: bool) -> str:
    """
    Определяем квадрант матрицы Эйзенхауэра.
    """
    if is_important and is_urgent:
        return "Q1"
    elif is_important and not is_urgent:
        return "Q2"
    elif not is_important and is_urgent:
        return "Q3"
    else:
        return "Q4"
