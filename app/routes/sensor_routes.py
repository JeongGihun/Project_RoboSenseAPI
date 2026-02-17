from fastapi import APIRouter, Depends, status, HTTPException, Query
from app.models.sensor import SensorResponse, SensorDataCreate, SensorListResponse, FilteredSensorResponse
from app.database import get_db, async_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import SensorData
from sqlalchemy import select
from typing import Optional
from app.redis_client import get_redis
from collections import deque
import logging, time, asyncio
from datetime import datetime, timedelta
import sensor_cpp

router = APIRouter()
logger = logging.getLogger(__name__)

last_invalidation = {}
sensor_queue = deque()
queue_lock = asyncio.Lock()


@router.post('/api/sensors', status_code=status.HTTP_201_CREATED)
async def collect_sensor_data(data: SensorDataCreate):
    try:
        redis = get_redis()
        now = time.time()

        sensors_to_add = [
            SensorData(
                robot_id=data.robot_id,
                sensor_type=sensor_item.sensor_type,
                timestamp=data.timestamp,
                raw_data=sensor_cpp.serialize_sensor_data(
                    sensor_item.data,
                    sensor_item.sensor_type
                ) if sensor_item.data else None
            )
            for sensor_item in data.sensors
        ]

        async with queue_lock:
            sensor_queue.extend(sensors_to_add)

        # 캐시 무효화
        if now - last_invalidation.get(data.robot_id, 0) > 10:
            await redis.delete(f"robot:{data.robot_id}:detail")
            last_invalidation[data.robot_id] = now

        # ← 이거 추가!
        if now - last_invalidation.get('stats', 0) > 60:
            await redis.delete("stats:recent")
            last_invalidation['stats'] = now

        return {
            "status": "success",
            "robot_id": data.robot_id,
            "queued_count": len(data.sensors)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"센서 데이터 등록 실패: {str(e)}")


@router.get('/api/sensors', response_model=SensorListResponse, status_code=status.HTTP_200_OK)
async def check_filter_data(
        limit: int = 100,
        robot_id: Optional[int] = None,
        sensor_type: Optional[str] = None,
        cursor_id: Optional[int] = None,
        db: AsyncSession = Depends(get_db)):
    query = select(SensorData).order_by(SensorData.id.desc())

    if cursor_id:
        query = query.where(cursor_id > SensorData.id)
    if robot_id:
        query = query.where(SensorData.robot_id == robot_id)
    if sensor_type:
        query = query.where(SensorData.sensor_type == sensor_type)

    query = query.limit(limit + 1)
    result = await db.execute(query)
    sensors = result.scalars().all()

    has_more = len(sensors) > limit
    if has_more:
        sensors = sensors[:limit]
    next_cursor = sensors[-1].id if sensors and has_more else None

    return {
        "data": sensors,
        "next_cursor": next_cursor,
        "has_more": has_more
    }

@router.get('/api/sensors/filtered', response_model=FilteredSensorResponse, status_code=status.HTTP_200_OK)
async def check_filter_sensor_data(
        robot_id : int , sensor_type : str,
        field : str, window_size : int, db : AsyncSession = Depends(get_db)):
    query = select(SensorData).where(SensorData.robot_id == robot_id)
    query = query.where(SensorData.sensor_type == sensor_type)
    query = query.where(SensorData.timestamp >= datetime.now() - timedelta(minutes=1))
    query = query.order_by(SensorData.timestamp.asc())

    result = await db.execute(query)
    sensors = result.scalars().all()

    if not sensors:
        return {
            "robot_id": robot_id,
            "sensor_type": sensor_type,
            "field": field,
            "original_data": [],
            "filtered_data": [],
            "window_size": window_size
        }

    parts = field.split(".")

    # 센서에서 값 추출
    original_data = []
    for sensor in sensors :
        if sensor.raw_data is None :
            continue

        try :
            if len(parts) == 1 :
                # GPS, LiDAR은 1개 필요
                value = sensor.raw_data[parts[0]]
            else :
                value = sensor.raw_data[parts[0]][parts[1]]

            original_data.append(float(value))

        except (KeyError, TypeError) :
            continue

    # C++ 버전 (비교용)
    #filtered_data = sensor_cpp.moving_average(original_data, window_size)

    # Python 버전 (비교용)
    def moving_average_python(data, window_size):
        result = []
        for i in range(len(data) - window_size + 1):
            window = data[i:i + window_size]
            result.append(sum(window) / window_size)
        return result

    filtered_data = moving_average_python(original_data, window_size)

    return {
        "robot_id": robot_id,
        "sensor_type": sensor_type,
        "field": field,
        "original_data": original_data,
        "filtered_data": filtered_data,
        "window_size": window_size
    }

@router.get('/api/sensors/{id}', response_model=SensorResponse, status_code=status.HTTP_200_OK)
async def check_filter_specific_data(id: int, db: AsyncSession = Depends(get_db)):
    query = select(SensorData)
    query = query.where(SensorData.id == id)
    result = await db.execute(query)
    sensor = result.scalar_one_or_none()
    if sensor is None:
        raise HTTPException(status_code=404, detail="해당 로봇의 센서 데이터는 존재하지 않음")
    return sensor


async def batch_commit_worker():
    """1초마다 큐에서 꺼내서 일괄 커밋"""

    while True:
        try:
            await asyncio.sleep(0.3)

            async with queue_lock:
                if not sensor_queue:
                    batch = []
                else:
                    batch = list(sensor_queue)
                    sensor_queue.clear()

            if not batch:
                continue

            async with async_session() as session:
                session.add_all(batch)
                await session.commit()

        except Exception as e:
            logger.error(f"배치 커밋 실패: {str(e)}")