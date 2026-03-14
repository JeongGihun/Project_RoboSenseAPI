from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os, logging, asyncpg
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

asyncpg_pool = None

#뒤에 있는것은 변수. 실제 값이 아님
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

POSTGRES_REPLICA_HOST=os.getenv("POSTGRES_REPLICA_HOST")
POSTGRES_REPLICA_PORT=os.getenv("POSTGRES_REPLICA_PORT")
POSTGRES_REPLICA_USER=os.getenv("POSTGRES_REPLICA_USER")
POSTGRES_REPLICA_PASSWORD=os.getenv("POSTGRES_REPLICA_PASSWORD")
POSTGRES_REPLICA_DB=os.getenv("POSTGRES_REPLICA_DB")
SQLALCHEMY_REPLICA_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_REPLICA_USER}:{POSTGRES_REPLICA_PASSWORD}@{POSTGRES_REPLICA_HOST}:{POSTGRES_REPLICA_PORT}/{POSTGRES_REPLICA_DB}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, pool_size=10, max_overflow=50, pool_timeout=30, pool_recycle=3600, pool_pre_ping=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

if POSTGRES_REPLICA_HOST:
    # Replica 설정 시
    engine_replica = create_async_engine(SQLALCHEMY_REPLICA_DATABASE_URL, echo=False, pool_size=10, max_overflow=50, pool_timeout=30, pool_recycle=3600, pool_pre_ping=True)
    async_session_replica = sessionmaker(engine_replica, class_=AsyncSession, expire_on_commit=False)
else :
    # Replica 없으면 Primary로 실행
    engine_replica = engine
    async_session_replica = async_session

Base = declarative_base()

async def get_db() :
    async with async_session() as session :
        yield session

async def get_replica_db() :
    async with async_session_replica() as session_replica :
        yield session_replica

def get_asyncpg_pool() :
    return asyncpg_pool

async def init_asyncpg_pool() :
    """시작"""
    global asyncpg_pool
    asyncpg_pool = await asyncpg.create_pool(host = POSTGRES_HOST, port = POSTGRES_PORT,
    user = POSTGRES_USER, password = POSTGRES_PASSWORD, database = POSTGRES_DB, min_size=10, max_size=50)

async def close_asyncpg_pool() :
    """종료"""
    global asyncpg_pool
    asyncpg_pool.close()
    await asyncpg_pool.wait_closed()