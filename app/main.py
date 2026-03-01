from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from app.routes import sensor_routes, robot_routes, stats_routes
from app.database import engine, Base
from contextlib import asynccontextmanager
from app.redis_client import connect_redis, close_redis, get_redis
import asyncio, cProfile, pstats, time, os
from pathlib import Path

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn :
        await conn.run_sync(Base.metadata.create_all)
    await connect_redis()
    for _ in range(2) :
        asyncio.create_task(sensor_routes.batch_commit_worker())
    yield
    await close_redis()

app = FastAPI(
    title = "RobosenseAPI",
    description = "로봇 센서 데이터 수집 API",
    version = "1.0.0",
    lifespan = lifespan
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(sensor_routes.router)
app.include_router(robot_routes.router)
app.include_router(stats_routes.router)

@app.get("/")
def root() :
    return {"message" : "Hi"}

@app.get("/health_check")
def health() :
    return {"health" : "Ok"}