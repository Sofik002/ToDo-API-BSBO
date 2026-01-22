from .tasks import router as tasks_router
from .stats import router as stats_router
from .auth import router as auth_router
from .admin import router as admin_router

__all__ = ["tasks_router", "stats_router", "auth_router", "admin_router"]