from fastapi import APIRouter, Depends, status, HTTPException, Query
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import SensorData, Robot
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timezone, timedelta
from app.models.enum import SensorName
from app.redis_client import get_redis
import json

router = APIRouter(prefix="/api", tags=["통계"])

#GET /stats (통계)

@router.get('/stats')
async def get_stats(
        start_time : Optional[datetime] = None,
        end_time : Optional[datetime] = None,
        db : AsyncSession = Depends(get_db)) :

    # redis 가져오기
    redis = get_redis()
    use_cache = (start_time is None and end_time is None)
    if use_cache :
        cache_key = "stats:recent"
        cached_stats = await redis.get(cache_key)
        if cached_stats :
            return json.loads(cached_stats)

    if start_time is None :
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
    if end_time is None :
        end_time = datetime.now(timezone.utc)
    query = select(SensorData).where(SensorData.created_at > start_time).where(SensorData.created_at <= end_time)
    result = await db.execute(query)
    sensors = result.scalars().all()

    # null 계산
    null_rates = {}

    for sensor_type in SensorName :
        specific_sensor_data = [data for data in sensors if data.sensor_type == sensor_type.value]

        if len(specific_sensor_data) == 0 :
            null_rates[sensor_type.value] = 0.0
            continue
        null_count = len([s for s in specific_sensor_data if s.raw_data is None])
        null_rate = null_count / len(specific_sensor_data)
        null_rates[sensor_type.value] = round(null_rate, 2)

    # robot 계산
    robot_query = select(Robot)
    robot_result = await db.execute(robot_query)
    robots = robot_result.scalars().all()

    total_robot = len(robots)
    active = len([r for r in robots if r.status == "active"])
    inactive = len([r for r in robots if r.status == "inactive"])
    inactive_robots = [
        {
            "robot_id" : r.id,
            "status" : r.status,
            "last_seen" : r.last_seen
        }
        for r in robots if r.status == "inactive"
    ]

    robot_summary = {
        "total_robot" : total_robot,
        "active" : active,
        "inactive" : inactive,
        "status_details" : inactive_robots
    }

    response_data = {
            "timestamp": datetime.now(timezone.utc),
            "time_range": {
                "start": start_time,
                "end": end_time
            },
            "null_rates": null_rates,
            "robot_summary": robot_summary
        }

    # 캐싱
    if use_cache :
        await redis.setex("stats:recent", 60, json.dumps(response_data, default=str))
    return response_data

## 여기 검토 다시받아야함