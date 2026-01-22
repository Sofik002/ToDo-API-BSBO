# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ToDo API",
    description="API для задач с матрицей Эйзенхауэра и аутентификацией",
    version="2.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    from database import init_db
    await init_db()

    # Импортируем роутеры
    from routers.tasks import router as tasks_router
    from routers.stats import router as stats_router
    from routers.auth import router as auth_router
    from routers.admin import router as admin_router

    # Подключаем роутеры
    app.include_router(tasks_router, prefix="/api/v2")
    app.include_router(stats_router, prefix="/api/v2")
    app.include_router(auth_router, prefix="/api/v2")
    app.include_router(admin_router, prefix="/api/v2")

@app.get("/")
async def root():
    return {"message": "ToDo API с аутентификацией работает", "version": "2.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)