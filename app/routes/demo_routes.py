"""BFF 프록시 라우트.

랜딩페이지(브라우저)가 API Key 없이 호출하는 데모용 엔드포인트.
내부에서 기존 `/api/*` 핸들러를 그대로 호출 — 인증만 우회.

API Key는 서버-to-서버 인증 용도이므로 브라우저 노출 금지.
데모 페이지는 이 프록시로 흘리고, 실제 `/api/*` 는 API Key 보호 유지.

파괴적 작업(`DELETE /api/reset`)은 의도적으로 프록시하지 않음 — admin 전용.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.robot import RobotCreate, RobotResponse, RobotDetailResponse, RobotStatusUpdate
from app.models.sensor import SensorDataCreate, SensorListResponse, SensorResponse, FilteredSensorResponse
from app.routes import robot_routes, sensor_routes, stats_routes

router = APIRouter(prefix="/demo", tags=["데모 (BFF)"])


@router.get("/robots", response_model=list[RobotResponse])
async def demo_list_robots(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await robot_routes.robot_data_list(status=status, db=db, _key=None)


@router.post("/robots", response_model=RobotResponse, status_code=status.HTTP_201_CREATED)
async def demo_register_robot(data: RobotCreate, db: AsyncSession = Depends(get_db)):
    return await robot_routes.registration_robot_data(data=data, db=db, _key=None)


@router.get("/robots/{id}", response_model=RobotDetailResponse)
async def demo_get_robot(id: int, db: AsyncSession = Depends(get_db)):
    return await robot_routes.robot_data_specific_list(id=id, db=db, _key=None)


@router.put("/robots/{robot_id}", response_model=RobotResponse)
async def demo_update_robot(
    robot_id: int,
    update_data: RobotStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await robot_routes.update_robot_status(
        robot_id=robot_id, update_data=update_data, db=db, _key=None
    )


@router.post("/sensors", status_code=status.HTTP_201_CREATED)
async def demo_collect_sensor(data: SensorDataCreate):
    return await sensor_routes.collect_sensor_data(data=data, _key=None)


@router.get("/sensors", response_model=SensorListResponse)
async def demo_list_sensors(
    limit: int = Query(100, ge=1, le=1000),
    robot_id: Optional[int] = None,
    sensor_type: Optional[str] = None,
    cursor_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    return await sensor_routes.check_filter_data(
        limit=limit, robot_id=robot_id, sensor_type=sensor_type,
        cursor_id=cursor_id, db=db, _key=None,
    )


@router.get("/sensors/filtered", response_model=FilteredSensorResponse)
async def demo_filtered_sensors(robot_id: int, sensor_type: str, field: str, window_size: int):
    return await sensor_routes.check_filter_sensor_data(
        robot_id=robot_id, sensor_type=sensor_type,
        field=field, window_size=window_size, _key=None,
    )


@router.get("/sensors/{id}", response_model=SensorResponse)
async def demo_get_sensor(id: int, db: AsyncSession = Depends(get_db)):
    return await sensor_routes.check_filter_specific_data(id=id, db=db, _key=None)


@router.get("/stats")
async def demo_stats(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    return await stats_routes.get_stats(
        start_time=start_time, end_time=end_time, db=db, _key=None,
    )
