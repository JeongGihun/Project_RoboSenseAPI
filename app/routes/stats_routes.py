from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import SensorData, Robot
from sqlalchemy import select, func, case
from typing import Optional
from datetime import datetime, timezone, timedelta
from app.models.enum import SensorName, Status
from app.redis_client import get_redis
import json, asyncio
import sensor_cpp

router = APIRouter(prefix="/api", tags=["통계"])

async def calculate_stats(
        db: AsyncSession,
        start_time : datetime,
        end_time : datetime
) -> dict :
    sensor_query = select(SensorData.sensor_type, func.count().label('total'), func.sum(
        case((SensorData.raw_data == None, 1), else_ = 0)).label('null_count')).where(
        SensorData.created_at > start_time, SensorData.created_at <= end_time
    ).group_by(SensorData.sensor_type)

    sensor_result = await db.execute(sensor_query)
    sensors_stats = sensor_result.all()

    # null 계산
    null_rates = sensor_cpp.calculate_null_rates(list(sensors_stats))

    for sensor_type in SensorName :
        if sensor_type.value not in null_rates :
            null_rates[sensor_type.value] = 0.0

    # robot 계산
    robot_query = select(Robot.status, func.count().label('count')).group_by(Robot.status)
    robot_result = await db.execute(robot_query)
    robots_stats = robot_result.all()

    robot_summary_base = sensor_cpp.calculate_robot_summary(list(robots_stats))

    inactive_query = select(Robot).where(Robot.status == 'inactive')
    inactive_result = await db.execute(inactive_query)
    inactive_robot_data = inactive_result.scalars().all()

    inactive_robots = [
        {
            "robot_id" : r.id,
            "status" : r.status.value,
            "last_seen" : r.last_seen
        }
        for r in inactive_robot_data
    ]

    robot_summary = {
        **robot_summary_base,
        "status_details" : inactive_robots
    }

    return {
            "timestamp": datetime.now(timezone.utc),
            "time_range": {
                "start": start_time,
                "end": end_time
            },
            "null_rates": null_rates,
            "robot_summary": robot_summary
        }

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
            ttl = await redis.ttl(cache_key)

            # 캐시 워밍. 10초 이하 남을 경우 갱신
            if ttl < 10 :
                asyncio.create_task(regenerate_stats_cache(db))
            return json.loads(cached_stats)

    if start_time is None :
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
    if end_time is None :
        end_time = datetime.now(timezone.utc)

    response_data = await calculate_stats(db, start_time, end_time)

    # 캐싱
    if use_cache :
        await redis.setex("stats:recent", 60, json.dumps(response_data, default=str))
    return response_data

async def regenerate_stats_cache(db: AsyncSession) :
    try :
        redis = get_redis()

        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        end_time = datetime.now(timezone.utc)

        response_data = await calculate_stats(db, start_time, end_time)
        await redis.setex("stats:recent", 60, json.dumps(response_data, default=str))

    except Exception as e :
        print(f"백그라운드 캐시 갱신 실패: {e}")

