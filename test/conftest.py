import os
import sys
import time
from unittest.mock import MagicMock, AsyncMock

os.environ.setdefault("ADMIN_KEY", "test-admin-key")

# sensor_cpp C++ 모듈 mock — 반드시 app import 전에 실행
mock_sensor_cpp = MagicMock()
mock_sensor_cpp.serialize_sensor_data.return_value = {"mocked": True}
mock_sensor_cpp.moving_average.return_value = [1.0, 2.0]
mock_sensor_cpp.calculate_null_rates.return_value = {}
mock_sensor_cpp.calculate_robot_summary.return_value = {
    "total": 0, "active": 0, "inactive": 0, "maintenance": 0
}
sys.modules["sensor_cpp"] = mock_sensor_cpp

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import app.redis_client as redis_module
import app.database as db_module
from app.main import app
from app.database import Base, get_db


class FakeRedis:
    """테스트용 in-memory Redis mock"""

    def __init__(self):
        self._data = {}
        self._ttls = {}

    def _check_expired(self, key):
        if key in self._ttls and self._ttls[key] < time.time():
            self._data.pop(key, None)
            self._ttls.pop(key, None)

    async def get(self, key):
        self._check_expired(key)
        val = self._data.get(key)
        return val if not isinstance(val, list) else None

    async def setex(self, key, ttl, value):
        self._data[key] = value
        self._ttls[key] = time.time() + ttl

    async def set(self, key, value, nx=False, ex=None):
        if nx:
            self._check_expired(key)
            if key in self._data:
                return None
        self._data[key] = value
        if ex is not None:
            self._ttls[key] = time.time() + ex
        return True

    async def delete(self, *keys):
        for key in keys:
            self._data.pop(key, None)
            self._ttls.pop(key, None)

    async def lpush(self, key, *values):
        if key not in self._data or not isinstance(self._data[key], list):
            self._data[key] = []
        for v in values:
            self._data[key].insert(0, v)

    async def ltrim(self, key, start, stop):
        if key in self._data and isinstance(self._data[key], list):
            self._data[key] = self._data[key][start:stop + 1]

    async def lrange(self, key, start, stop):
        self._check_expired(key)
        if key not in self._data or not isinstance(self._data[key], list):
            return []
        if stop == -1:
            return self._data[key][start:]
        return self._data[key][start:stop + 1]

    async def expire(self, key, ttl):
        self._ttls[key] = time.time() + ttl

    async def ttl(self, key):
        if key not in self._ttls:
            return -1
        remaining = self._ttls[key] - time.time()
        return max(0, int(remaining))

    async def ping(self):
        return True

    async def flushdb(self):
        self._data.clear()
        self._ttls.clear()

    async def flushall(self):
        self._data.clear()
        self._ttls.clear()


# SQLite in-memory 테스트 엔진
test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
)

TestSession = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """매 테스트마다 테이블 생성/삭제"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """테스트용 DB 세션"""
    async with TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """테스트용 AsyncClient — DB와 Redis를 mock으로 교체"""

    # get_db는 FastAPI Depends이므로 dependency_overrides 사용
    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # get_redis는 직접 호출이므로 모듈 변수 교체
    fake_redis = FakeRedis()
    original_redis = redis_module.redis_client
    redis_module.redis_client = fake_redis

    # asyncpg_pool은 health_check에서 사용 — mock 주입
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value=1)
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
    original_pool = db_module.asyncpg_pool
    db_module.asyncpg_pool = mock_pool

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 테스트용 API Key 자동 발급
        issue_resp = await ac.post(
            "/admin/api-keys",
            json={"robot_id": None},
            headers={"X-Admin-Key": os.environ["ADMIN_KEY"]},
        )
        if issue_resp.status_code == 201:
            ac.headers["X-API-Key"] = issue_resp.json()["api_key"]
        yield ac

    # 정리
    app.dependency_overrides.clear()
    redis_module.redis_client = original_redis
    db_module.asyncpg_pool = original_pool
