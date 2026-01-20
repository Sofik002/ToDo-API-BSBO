# main.py
from fastapi import FastAPI
from routers import stats, tasks

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={"name": "София"}
)

# УБРАТЬ startup_event - таблицы уже созданы!
# @app.on_event("startup")
# async def startup_event():
#     print("🚀 Запуск приложения...")
#     await init_db()  # ← УБРАТЬ эту строку!
#     print("✅ База данных готова")

app.include_router(tasks.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "ToDo API с матрицей Эйзенхауэра"}

@app.get("/health")
async def health():
    return {"status": "healthy"}