"""센서 데이터 API 테스트 (D1-D2)"""
from datetime import datetime, timezone

from app.models.db_models import Robot, SensorData


# === POST /api/sensors ===

async def test_post_sensor_success(client, db_session):
    """정상 센서 데이터 수집"""
    robot = Robot(name="TestBot", model="v1", status="active", battery_level=80)
    db_session.add(robot)
    await db_session.commit()

    response = await client.post("/api/sensors", json={
        "robot_id": robot.id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sensors": [
            {"sensor_type": "IMU", "data": {
                "acceleration": {"x": 1.0, "y": 2.0, "z": 3.0},
                "gyroscope": {"x": 0.1, "y": 0.2, "z": 0.3}
            }}
        ]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["queued_count"] == 1


async def test_post_sensor_invalid_body(client):
    """필수 필드 누락 시 422"""
    response = await client.post("/api/sensors", json={})
    assert response.status_code == 422


async def test_post_sensor_empty_sensors_list(client, db_session):
    """빈 센서 리스트"""
    robot = Robot(name="TestBot", model="v1", status="active", battery_level=80)
    db_session.add(robot)
    await db_session.commit()

    response = await client.post("/api/sensors", json={
        "robot_id": robot.id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sensors": []
    })
    assert response.status_code == 201
    assert response.json()["queued_count"] == 0


# === GET /api/sensors ===

async def test_get_sensors_empty(client):
    """데이터 없을 때 빈 리스트"""
    response = await client.get("/api/sensors")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["has_more"] is False


async def test_get_sensors_with_data(client, db_session):
    """데이터 있을 때 조회"""
    robot = Robot(name="TestBot", model="v1", status="active", battery_level=80)
    db_session.add(robot)
    await db_session.commit()

    sensor = SensorData(
        robot_id=robot.id, sensor_type="IMU",
        timestamp=datetime.now(timezone.utc),
        raw_data={"acceleration": {"x": 1.0}}
    )
    db_session.add(sensor)
    await db_session.commit()

    response = await client.get("/api/sensors")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["robot_id"] == robot.id


async def test_get_sensors_filter_robot_id(client, db_session):
    """robot_id 필터링"""
    r1 = Robot(name="Bot1", model="v1", status="active", battery_level=80)
    r2 = Robot(name="Bot2", model="v1", status="active", battery_level=90)
    db_session.add_all([r1, r2])
    await db_session.commit()

    s1 = SensorData(robot_id=r1.id, sensor_type="IMU", timestamp=datetime.now(timezone.utc))
    s2 = SensorData(robot_id=r2.id, sensor_type="GPS", timestamp=datetime.now(timezone.utc))
    db_session.add_all([s1, s2])
    await db_session.commit()

    response = await client.get(f"/api/sensors?robot_id={r1.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["robot_id"] == r1.id


async def test_get_sensors_filter_sensor_type(client, db_session):
    """sensor_type 필터링"""
    robot = Robot(name="Bot", model="v1", status="active", battery_level=80)
    db_session.add(robot)
    await db_session.commit()

    s1 = SensorData(robot_id=robot.id, sensor_type="IMU", timestamp=datetime.now(timezone.utc))
    s2 = SensorData(robot_id=robot.id, sensor_type="GPS", timestamp=datetime.now(timezone.utc))
    db_session.add_all([s1, s2])
    await db_session.commit()

    response = await client.get("/api/sensors?sensor_type=GPS")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["sensor_type"] == "GPS"


async def test_get_sensors_pagination(client, db_session):
    """커서 기반 페이지네이션"""
    robot = Robot(name="Bot", model="v1", status="active", battery_level=80)
    db_session.add(robot)
    await db_session.commit()

    for i in range(5):
        db_session.add(SensorData(
            robot_id=robot.id, sensor_type="IMU",
            timestamp=datetime.now(timezone.utc)
        ))
    await db_session.commit()

    # 첫 페이지 (limit=2)
    resp1 = await client.get("/api/sensors?limit=2")
    assert resp1.status_code == 200
    d1 = resp1.json()
    assert len(d1["data"]) == 2
    assert d1["has_more"] is True
    assert d1["next_cursor"] is not None

    # 두 번째 페이지
    resp2 = await client.get(f"/api/sensors?limit=2&cursor_id={d1['next_cursor']}")
    assert resp2.status_code == 200
    d2 = resp2.json()
    assert len(d2["data"]) == 2
    # 첫 페이지와 겹치지 않아야 함
    ids1 = {s["id"] for s in d1["data"]}
    ids2 = {s["id"] for s in d2["data"]}
    assert ids1.isdisjoint(ids2)


# === GET /api/sensors/{id} ===

async def test_get_sensor_by_id_success(client, db_session):
    """개별 센서 조회 성공"""
    robot = Robot(name="Bot", model="v1", status="active", battery_level=80)
    db_session.add(robot)
    await db_session.commit()

    sensor = SensorData(
        robot_id=robot.id, sensor_type="GPS",
        timestamp=datetime.now(timezone.utc),
        raw_data={"latitude": 37.5, "longitude": 127.0}
    )
    db_session.add(sensor)
    await db_session.commit()

    response = await client.get(f"/api/sensors/{sensor.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sensor.id
    assert data["sensor_type"] == "GPS"


async def test_get_sensor_by_id_not_found(client):
    """존재하지 않는 센서 ID → 404"""
    response = await client.get("/api/sensors/99999")
    assert response.status_code == 404
