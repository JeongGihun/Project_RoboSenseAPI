"""통계 API 테스트 (D2)"""
from datetime import datetime, timezone

from app.models.db_models import Robot, SensorData


async def test_get_stats_default(client, db_session):
    """기본 통계 조회 (시간 파라미터 없음)"""
    response = await client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "time_range" in data
    assert "null_rates" in data
    assert "robot_summary" in data


async def test_get_stats_with_time_range(client, db_session):
    """커스텀 시간 범위 통계"""
    start = "2026-01-01T00:00:00Z"
    end = "2026-12-31T23:59:59Z"
    response = await client.get(f"/api/stats?start_time={start}&end_time={end}")
    assert response.status_code == 200
    data = response.json()
    assert "time_range" in data


async def test_get_stats_with_data(client, db_session):
    """데이터 있을 때 통계"""
    robot = Robot(name="Bot", model="v1", status="active", battery_level=80)
    db_session.add(robot)
    await db_session.commit()

    sensor = SensorData(
        robot_id=robot.id, sensor_type="IMU",
        timestamp=datetime.now(timezone.utc),
        raw_data={"acceleration": {"x": 1.0}}
    )
    db_session.add(sensor)
    await db_session.commit()

    response = await client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "null_rates" in data
