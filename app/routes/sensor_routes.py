from fastapi import APIRouter, Depends
from app.models.sensor import SensorDataCreate
from typing import Optional
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import SensorData
from sqlalchemy import select

router = APIRouter()

#POST /api/sensors (센서 데이터 수집)
#GET /api/sensors (데이터 조회 + 필터링)

@router.post('/api/sensors')
async def collect_sensor_data(data : SensorDataCreate, db : AsyncSession = Depends(get_db)) :
    db_sensor = SensorData(
        robot_id=data.robot_id,
        timestamp=data.timestamp,
        sensors=data.model_dump()["sensors"]
    )
    db.add(db_sensor)
    await db.commit()
    return {"status" : "success", "inserted_count" : len(data.sensors), "robot_id" : data.robot_id}

@router.get('/api/sensors')
async def check_filter_data(robot_id : Optional[int] = None, db : AsyncSession = Depends(get_db)) :
    query = select(SensorData)
    if robot_id :
        query = query.where(SensorData.robot_id == robot_id)
    result = await db.execute(query)
    sensors = result.scalars().all()
    return sensors