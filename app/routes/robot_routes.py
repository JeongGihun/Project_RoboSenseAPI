from fastapi import APIRouter, Depends, HTTPException, status
from app.models.robot import RobotCreate, RobotResponse, SensorInRobot, RobotDetailResponse
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import Robot, SensorData
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

router = APIRouter()

# POST /api/robots (로봇 등록 = 생성)
# GET /api/robots (로봇 목록)
# GET /api/robots/{id} (특정 로봇)

@router.post('/api/robots', response_model = RobotResponse, status_code = status.HTTP_201_CREATED)
async def registration_robot_data(data : RobotCreate, db : AsyncSession = Depends(get_db)) :
    try :
        db_robot = Robot(
            name  = data.name,
            model = data.model,
            status = data.status,
            battery_level = data.battery_level
        )
        db.add(db_robot)
        await db.commit()
        await db.refresh(db_robot)
        return db_robot
    except Exception as e :
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"로봇 등록 실패 : {str(e)}")

@router.get('/api/robots', response_model = List[RobotResponse], status_code = status.HTTP_200_OK)
async def robot_data_list(db : AsyncSession = Depends(get_db)) :
    query = select(Robot)
    result = await db.execute(query)
    robots = result.scalars().all()
    return robots

@router.get('/api/robots/{id}', response_model = RobotDetailResponse, status_code = status.HTTP_200_OK)
async def robot_data_specific_list(id : int, db : AsyncSession = Depends(get_db)) :
    query = select(Robot).options(selectinload(Robot.sensor_data)).where(Robot.id == id)
    result = await db.execute(query)
    robot = result.scalar_one_or_none()
    if robot is None :
        raise HTTPException(status_code=404, detail="해당 로봇이 존재 하지 않음")
    recent_sensors = sorted(
        robot.sensor_data, key = lambda x : x.timestamp, reverse=True
    )[:10]

    return {
        "id" : robot.id,
        "name" : robot.name,
        "model" : robot.model,
        "status" : robot.status,
        "battery_level" : robot.battery_level,
        "last_seen" : robot.last_seen,
        "created_at" : robot.created_at,
        "recent_sensors" : [
            {
                "sensor_type": s.sensor_type,
                "timestamp" : s.timestamp,
                "raw_data" : s.raw_data
            }
            for s in recent_sensors
        ]
    }