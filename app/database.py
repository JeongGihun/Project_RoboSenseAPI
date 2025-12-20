from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:postgres123@localhost:5432/robosense_db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo = True)

async_session = sessionmaker(engine, class_ = AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db() :
    async with async_session() as session :
        yield session