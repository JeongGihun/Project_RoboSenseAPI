from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from app.routes import sensor_routes, robot_routes, stats_routes
from app.database import engine, Base, init_asyncpg_pool, close_asyncpg_pool
from app.middleware import RequestIDMiddleware
from app.logging_config import RequestIDFilter
from contextlib import asynccontextmanager
from app.redis_client import connect_redis, close_redis
import asyncio, logging
from app.context import request_id
from fastapi.responses import JSONResponse

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(request_id)s %(asctime)s [%(levelname)s] %(message)s"))
handler.addFilter(RequestIDFilter())

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(handler)

logger = logging.getLogger(__name__) # main의 경우

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        pass
    await connect_redis()
    await init_asyncpg_pool()
    for _ in range(2):
        asyncio.create_task(sensor_routes.batch_commit_worker())
    yield
    await close_asyncpg_pool()
    await close_redis()

app = FastAPI(
    title = "RobosenseAPI",
    description = "로봇 센서 데이터 수집 API",
    version = "1.0.0",
    lifespan = lifespan
)

# 미들웨어는 코드 순서의 역순. 주의.
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestIDMiddleware)

app.include_router(sensor_routes.router)
app.include_router(robot_routes.router)
app.include_router(stats_routes.router)

@app.get("/")
def root() :
    return {"message" : "Hi"}

@app.get("/health_check")
def health() :
    return {"health" : "Ok"}

@app.exception_handler(Exception)
async def exception_handler(request, exc) :
    logger.error(f"request_id: {request_id.get()} | {request.method} {request.url} | {type(exc).__name__}: {exc}")
    info = {"status": "error", "message": "Internal server error"}
    return JSONResponse(status_code=500, content=info)