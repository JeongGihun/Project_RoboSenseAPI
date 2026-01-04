import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from app.database import Base, engine
from app.models.db_models import Robot, SensorData

async def reset_database():
    print("기존 테이블 삭제")
    async with engine.begin() as conn :
        await conn.run_sync(Base.metadata.drop_all)

    print("테이블 및 인덱스 재생성")
    async with engine.begin() as conn :
        await conn.run_sync(Base.metadata.create_all)

    print("테이블 및 인덱스 재생성 완료")

    await engine.dispose()

if __name__ == "__main__" :
    asyncio.run(reset_database())