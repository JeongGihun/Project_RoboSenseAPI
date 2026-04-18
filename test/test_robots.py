"""로봇 API 테스트 (D2)"""
from datetime import datetime, timezone

from app.models.db_models import Robot, SensorData


# === POST /api/robots ===

async def test_register_robot(client):
    """로봇 등록 성공"""
    response = await client.post("/api/robots", json={
        "name": "TestBot", "model": "v1",
        "status": "active", "battery_level": 80
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "TestBot"
    assert data["status"] == "active"
    assert data["battery_level"] == 80
    assert "id" in data


async def test_register_robot_invalid_battery(client):
    """배터리 0~100 범위 초과 시 422"""
    response = await client.post("/api/robots", json={
        "name": "TestBot", "model": "v1",
        "status": "active", "battery_level": 150
    })
    assert response.status_code == 422


async def test_register_robot_missing_name(client):
    """필수 필드 누락 시 422"""
    response = await client.post("/api/robots", json={
        "model": "v1", "status": "active", "battery_level": 80
    })
    assert response.status_code == 422


# === GET /api/robots ===

async def test_list_robots_empty(client):
    """로봇 없을 때 빈 리스트"""
    response = await client.get("/api/robots")
    assert response.status_code == 200
    assert response.json() == []


async def test_list_robots_with_data(client, db_session):
    """로봇 목록 조회"""
    r1 = Robot(name="Bot1", model="v1", status="active", battery_level=80)
    r2 = Robot(name="Bot2", model="v2", status="inactive", battery_level=50)
    db_session.add_all([r1, r2])
    await db_session.commit()

    response = await client.get("/api/robots")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


async def test_list_robots_filter_status(client, db_session):
    """상태 필터링"""
    r1 = Robot(name="Bot1", model="v1", status="active", battery_level=80)
    r2 = Robot(name="Bot2", model="v2", status="inactive", battery_level=50)
    db_session.add_all([r1, r2])
    await db_session.commit()

    response = await client.get("/api/robots?status=active")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "active"


# === GET /api/robots/{id} ===

async def test_get_robot_detail(client, db_session):
    """로봇 상세 조회 (최근 센서 포함)"""
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

    response = await client.get(f"/api/robots/{robot.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == robot.id
    assert data["name"] == "Bot"
    assert "recent_sensors" in data


async def test_get_robot_not_found(client):
    """존재하지 않는 로봇 ID → 404"""
    response = await client.get("/api/robots/99999")
    assert response.status_code == 404


# === PUT /api/robots/{id} ===

async def test_update_robot_status(client, db_session):
    """로봇 상태 업데이트 성공"""
    robot = Robot(name="Bot", model="v1", status="active", battery_level=80)
    db_session.add(robot)
    await db_session.commit()

    response = await client.put(f"/api/robots/{robot.id}", json={
        "status": "maintenance", "battery_level": 30
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "maintenance"
    assert data["battery_level"] == 30


async def test_update_robot_not_found(client):
    """존재하지 않는 로봇 업데이트 → 404"""
    response = await client.put("/api/robots/99999", json={
        "status": "active", "battery_level": 50
    })
    assert response.status_code == 404


async def test_update_robot_invalid_battery(client, db_session):
    """배터리 범위 초과 업데이트 → 422"""
    robot = Robot(name="Bot", model="v1", status="active", battery_level=80)
    db_session.add(robot)
    await db_session.commit()

    response = await client.put(f"/api/robots/{robot.id}", json={
        "status": "active", "battery_level": 200
    })
    assert response.status_code == 422
