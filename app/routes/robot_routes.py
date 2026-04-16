from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.robot import RobotCreate, RobotResponse, SensorInRobot, RobotDetailResponse, RobotStatusUpdate
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import Robot, SensorData
from sqlalchemy import select, delete, text
from typing import List, Optional
from app.redis_client import get_redis
from app.auth import verify_api_key
from app.exceptions import RobotNotFoundError
from datetime import datetime, timezone
import json

router = APIRouter()

# POST /api/robots (로봇 등록 = 생성)
# GET /api/robots (로봇 목록)
# GET /api/robots/{id} (특정 로봇)

@router.post('/api/robots', response_model = RobotResponse, status_code = status.HTTP_201_CREATED)
async def registration_robot_data(data : RobotCreate, db : AsyncSession = Depends(get_db), _key=Depends(verify_api_key)) :
    try :
        # redis 가져오기
        redis = get_redis()

        db_robot = Robot(
            name  = data.name,
            model = data.model,
            status = data.status,
            battery_level = data.battery_level
        )
        db.add(db_robot)
        await db.commit()

        # 캐시 무효화
        await redis.delete("robots:all")
        await redis.delete(f"robots:status:{data.status}")
        return db_robot

    except Exception as e :
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"로봇 등록 실패 : {str(e)}")

@router.put('/api/robots/{robot_id}', response_model=RobotResponse, status_code = status.HTTP_200_OK)
async def update_robot_status(robot_id : int, update_data : RobotStatusUpdate, db : AsyncSession = Depends(get_db), _key=Depends(verify_api_key)) :
    try :
        redis = get_redis()

        query = select(Robot).where(Robot.id == robot_id)
        result = await db.execute(query)
        robot = result.scalar_one_or_none()

        if robot is None :
            raise RobotNotFoundError({"robot_id": robot_id})

        old_status = robot.status
        robot.status = update_data.status
        robot.battery_level = update_data.battery_level
        robot.last_seen = datetime.now(timezone.utc)

        await db.commit()

        await redis.delete(f"robot:{robot_id}:detail")
        await redis.delete("robots:all")
        await redis.delete(f"robots:status:{old_status.value}")
        await redis.delete(f"robots:status:{update_data.status.value}")

        return robot

    except (HTTPException, RobotNotFoundError) :
        raise
    except Exception as e :
        await db.rollback()
        raise HTTPException(status_code=500, detail = f"로봇 상태 업데이트 실패 : {str(e)}")


@router.get('/api/robots', response_model = List[RobotResponse], status_code = status.HTTP_200_OK)
async def robot_data_list(
        status : Optional[str] = Query(None, description = "Filter by robot status"),
        db : AsyncSession = Depends(get_db),
        _key=Depends(verify_api_key)) :
    # redis 가져오기
    redis = get_redis()
    if status :
        cache_key = f"robots:status:{status}"
    else :
        cache_key = "robots:all"

    # 캐시 확인
    cached_robots = await redis.get(cache_key)
    if cached_robots :
        return json.loads(cached_robots)

    query = select(Robot)
    if status :
        query = query.where(Robot.status == status)

    result = await db.execute(query)
    robots = result.scalars().all()
    robots_data = [
        {
            "id" : r.id,
            "name" : r.name,
            "model" : r.model,
            "status" : r.status,
            "battery_level" : r.battery_level,
            "last_seen" : r.last_seen,
            "created_at" : r.created_at
        }
        for r in robots
    ]
    # 캐싱
    await redis.setex(cache_key, 600, json.dumps(robots_data, default=str))

    return robots_data

@router.get('/api/robots/{id}', response_model = RobotDetailResponse, status_code = status.HTTP_200_OK)
async def robot_data_specific_list(id : int, db : AsyncSession = Depends(get_db), _key=Depends(verify_api_key)) :
    # redis 가져오기
    redis = get_redis()
    cache_key = f"robot:{id}:detail"

    # 캐시 확인
    cached_robot = await redis.get(cache_key)
    if cached_robot :
        return json.loads(cached_robot)

    query = select(Robot).where(Robot.id == id)
    result = await db.execute(query)
    robot = result.scalar_one_or_none()

    if robot is None :
        raise RobotNotFoundError({"robot_id": id})

    sensor_query = (select(SensorData).where(SensorData.robot_id == id).order_by(SensorData.timestamp.desc()).limit(10))
    sensor_result = await db.execute(sensor_query)
    recent_sensors = sensor_result.scalars().all()

    response_data = {
        "id": robot.id,
        "name": robot.name,
        "model": robot.model,
        "status": robot.status,
        "battery_level": robot.battery_level,
        "last_seen": robot.last_seen,
        "created_at": robot.created_at,
        "recent_sensors": [
            {
                "sensor_type": s.sensor_type,
                "timestamp": s.timestamp,
                "raw_data": s.raw_data
            }
            for s in recent_sensors
        ]
    }
    # 캐싱
    await redis.setex(cache_key,5, json.dumps(response_data, default = str))

    return response_data


@router.delete('/api/reset', status_code = status.HTTP_200_OK)
async def reset_all_data(db : AsyncSession = Depends(get_db), _key=Depends(verify_api_key)) :
    """모든 센서 데이터와 로봇 데이터를 초기화합니다."""
    try :
        redis = get_redis()

        # 센서 데이터 먼저 삭제 (FK 제약조건)
        await db.execute(delete(SensorData))
        # 로봇 데이터 삭제
        await db.execute(delete(Robot))
        # ID 시퀀스 1부터 재시작
        await db.execute(text("ALTER SEQUENCE robots_id_seq RESTART WITH 1"))
        await db.execute(text("ALTER SEQUENCE sensor_data_id_seq RESTART WITH 1"))
        await db.commit()

        # Redis 캐시 전체 초기화
        await redis.flushdb()

        return {"message" : "모든 데이터가 초기화되었습니다.", "status" : "success"}

    except Exception as e :
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"데이터 초기화 실패 : {str(e)}")