from fastapi import FastAPI
from routers import tasks, stats  

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={"name": "София"}
)

app.include_router(tasks.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")