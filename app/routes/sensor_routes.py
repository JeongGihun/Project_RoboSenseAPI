from fastapi import APIRouter, Depends, status, HTTPException, Query
from app.models.sensor import SensorResponse, SensorDataCreate, SensorListResponse
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import SensorData
from sqlalchemy import select
from typing import Optional
from app.redis_client import get_redis
import logging
import time

router = APIRouter()
logger = logging.getLogger(__name__)

last_invalidation = {}
#POST /api/sensors (센서 데이터 수집)
#GET /api/sensors (데이터 조회 + 필터링)
#GET /api/sensors?robot_id=1 (특정 로봇 데이터 조회 + 필터링)

@router.post('/api/sensors', status_code = status.HTTP_201_CREATED)
async def collect_sensor_data(data : SensorDataCreate, db : AsyncSession = Depends(get_db)) :
    try :
        # redis 가져오기
        redis = get_redis()
        now = time.time()

        # Bulk insert
        sensors_to_add = [
            SensorData(
                robot_id = data.robot_id,
                sensor_type=sensor_item.sensor_type,
                timestamp=data.timestamp,
                raw_data=sensor_item.data.model_dump() if sensor_item.data else None
            )
            for sensor_item in data.sensors
        ]
        db.add_all(sensors_to_add)
        await db.commit()
        # 캐시 무효화
        if now - last_invalidation.get(data.robot_id, 0) > 10 :
            await redis.delete(f"robot:{data.robot_id}:detail")
            last_invalidation[data.robot_id] = now

        if now - last_invalidation.get('stats', 0) > 60 :
            await redis.delete("stats:recent")
            last_invalidation['stats'] = now
        return {
            "status" : "success",
            "inserted_count" : len(data.sensors),
            "robot_id" : data.robot_id
        }
    except Exception as e :
        await db.rollback()
        raise HTTPException(status_code=500, detail = f"센서 데이터 등록 실패 : {str(e)}")

@router.get('/api/sensors', response_model = SensorListResponse, status_code = status.HTTP_200_OK)
async def check_filter_data(
        limit : int = 100,
        robot_id : Optional[int] = None,
        sensor_type : Optional[str] = None,
        cursor_id : Optional[int] = None,
        db : AsyncSession = Depends(get_db)) :
    query = select(SensorData).order_by(SensorData.id.desc())

    if cursor_id :
        query = query.where(cursor_id > SensorData.id)
    if robot_id :
        query = query.where(SensorData.robot_id == robot_id)
    if sensor_type :
        query = query.where(SensorData.sensor_type == sensor_type)

    query = query.limit(limit+1)
    result = await db.execute(query)
    sensors = result.scalars().all()

    has_more = len(sensors) > limit
    if has_more :
        sensors = sensors[:limit]
    next_cursor = sensors[-1].id if sensors and has_more else None

    return {
        "data" : sensors,
        "next_cursor" : next_cursor,
        "has_more" : has_more
    }

@router.get('/api/sensors/{id}', response_model = SensorResponse, status_code = status.HTTP_200_OK)
async def check_filter_specific_data(id : int, db : AsyncSession = Depends(get_db)) :
    query = select(SensorData)
    query = query.where(SensorData.id == id)
    result = await db.execute(query)
    sensor = result.scalar_one_or_none()
    if sensor is None :
        raise HTTPException(status_code=404, detail = "해당 로봇의 센서 데이터는 존해 하지 않음")
    return sensor