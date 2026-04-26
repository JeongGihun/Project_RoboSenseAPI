"""랜딩페이지용 공개 조회 엔드포인트.

API Key 없이 접근 가능. **조회 전용**.
쓰기는 `/api/*` 에서만 가능 (서버-to-서버 통합은 API Key 필수).

왜 쓰기를 제공하지 않나:
- 익명 쓰기를 열면 봇·스크립트가 DB 오염 가능 (rate limit 없음)
- RoboSense는 로봇/IoT 기기 통합 API라 사람 로그인 개념이 없음
  → 쓰기 권한을 익명 브라우저 세션에 부여할 근거가 없음
- 조회만 공개하면 포트폴리오 시연 요구 + 보안 요구 둘 다 만족
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.robot import RobotResponse, RobotDetailResponse
from app.models.sensor import SensorListResponse, SensorResponse, FilteredSensorResponse
from app.routes import robot_routes, sensor_routes, stats_routes

router = APIRouter(prefix="/demo", tags=["랜딩페이지 공개 조회"])


@router.get("/robots", response_model=list[RobotResponse])
async def demo_list_robots(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await robot_routes.robot_data_list(status=status, db=db, _key=None)


@router.get("/robots/{id}", response_model=RobotDetailResponse)
async def demo_get_robot(id: int, db: AsyncSession = Depends(get_db)):
    return await robot_routes.robot_data_specific_list(id=id, db=db, _key=None)


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
