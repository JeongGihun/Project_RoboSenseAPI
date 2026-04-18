from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.routes import sensor_routes, robot_routes, stats_routes, admin_routes
from app.database import engine, Base, init_asyncpg_pool, close_asyncpg_pool, get_asyncpg_pool
from app.middleware import RequestIDMiddleware
from app.logging_config import RequestIDFilter
from contextlib import asynccontextmanager
from app.redis_client import connect_redis, close_redis, get_redis
import asyncio
import logging
import os
from datetime import datetime, timezone
from app.context import request_id
from app.metrics import get_metrics
from app.exceptions import BaseAPIException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from app.utils.retry import retry_connect

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
    await retry_connect(connect_redis, "Redis")
    await retry_connect(init_asyncpg_pool, "PostgreSQL")
    task_list = []
    for _ in range(2):
        task = asyncio.create_task(sensor_routes.batch_commit_worker())
        task_list.append(task)
    yield
    for _ in range(2) :
        await sensor_routes.sensor_queue.put(None)
    await asyncio.gather(*task_list)
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
allowed_origins = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8000",
    ).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensor_routes.router)
app.include_router(robot_routes.router)
app.include_router(stats_routes.router)
app.include_router(admin_routes.router)

@app.get("/", response_class=HTMLResponse)
def root() :
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    try :
        with open(index_path, "r", encoding="utf-8") as f :
            return HTMLResponse(content=f.read())
    except FileNotFoundError :
        return HTMLResponse(content="<h1>RoboSense API</h1><p>Landing page not found.</p>")

@app.get("/health")
@app.get("/health_check")
async def health() :
    db_ok = False
    redis_ok = False

    try :
        async with get_asyncpg_pool().acquire() as conn :
            await conn.fetchval("SELECT 1")
        db_ok = True
    except Exception:
        pass

    try :
        await get_redis().ping()
        redis_ok = True
    except Exception:
        pass

    if db_ok and redis_ok:
        return {"status": "healthy", "db": db_ok, "redis": redis_ok}
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "db": db_ok, "redis": redis_ok}
        )

@app.get("/metrics")
async def metrics():
    return get_metrics()


@app.exception_handler(BaseAPIException)
async def api_exception_handler(request, exc: BaseAPIException):
    logger.warning(f"request_id: {request_id.get()} | {exc.error_code}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "detail": exc.detail,
            "timestamp": exc.timestamp,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "요청 데이터 검증 실패",
            "detail": exc.errors(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    logger.error(f"request_id: {request_id.get()} | {request.method} {request.url} | {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "서버 내부 오류",
            "detail": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )