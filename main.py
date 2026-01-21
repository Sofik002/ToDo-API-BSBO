# main.py
from fastapi import FastAPI

app = FastAPI(
    title="ToDo API",
    description="API для задач с матрицей Эйзенхауэра",
    version="1.0.0",
)

@app.on_event("startup")
async def startup():
    from database import init_db
    await init_db()

    from routers.tasks import router as tasks_router
    from routers.stats import router as stats_router

    app.include_router(tasks_router, prefix="/api/v1")
    app.include_router(stats_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "API работает"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)