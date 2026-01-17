from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:yourpassword@localhost:5434/robosense_db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo = False, pool_size = 50, max_overflow = 50)

async_session = sessionmaker(engine, class_ = AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db() :
    async with async_session() as session :
        yield session