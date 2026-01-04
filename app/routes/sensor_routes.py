from fastapi import APIRouter, Depends, status, HTTPException
from app.models.sensor import SensorResponse, SensorDataCreate
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import SensorData
from sqlalchemy import select
from typing import List, Optional

router = APIRouter()

#POST /api/sensors (센서 데이터 수집)
#GET /api/sensors (데이터 조회 + 필터링)
#GET /api/sensors?robot_id=1 (특정 로봇 데이터 조회 + 필터링)

@router.post('/api/sensors', status_code = status.HTTP_201_CREATED)
async def collect_sensor_data(data : SensorDataCreate, db : AsyncSession = Depends(get_db)) :
    try :
        for sensor_item in data.sensors :
            db_sensor = SensorData(
                robot_id=data.robot_id,
                sensor_type=sensor_item.sensor_type,
                timestamp=data.timestamp,
                raw_data=sensor_item.data.model_dump() if sensor_item.data else None
            )
            db.add(db_sensor)
        await db.commit()
        return {
            "status" : "success",
            "inserted_count" : len(data.sensors),
            "robot_id" : data.robot_id
        }
    except Exception as e :
        await db.rollback()
        raise HTTPException(status_code=500, detail = f"센서 데이터 등록 실패 : {str(e)}")

@router.get('/api/sensors', response_model = List[SensorResponse], status_code = status.HTTP_200_OK)
async def check_filter_data(
        robot_id : Optional[int] = None,
        sensor_type : Optional[str] = None,
        db : AsyncSession = Depends(get_db)) :
    query = select(SensorData)
    if robot_id :
        query = query.where(SensorData.robot_id == robot_id)

    if sensor_type :
        query = query.where(SensorData.sensor_type == sensor_type)

    result = await db.execute(query)
    sensors = result.scalars().all()
    return sensors

@router.get('/api/sensors/{id}', response_model = SensorResponse, status_code = status.HTTP_200_OK)
async def check_filter_specific_data(id : int, db : AsyncSession = Depends(get_db)) :
    query = select(SensorData)
    query = query.where(SensorData.id == id)
    result = await db.execute(query)
    sensor = result.scalar_one_or_none()
    if sensor is None :
        raise HTTPException(status_code=404, detail = "해당 로봇의 센서 데이터는 존해 하지 않음")
    return sensor