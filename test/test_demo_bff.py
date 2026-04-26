"""demo 프록시 라우트 테스트.

랜딩페이지용 공개 **조회 전용** 엔드포인트. 쓰기는 여전히 `/api/*`(API Key 필요).
"""
from app.models.db_models import Robot


# === 읽기 허용 ===

async def test_demo_get_robots_empty(client):
    """키 없이 GET /demo/robots 호출 가능"""
    del client.headers["X-API-Key"]
    response = await client.get("/demo/robots")
    assert response.status_code == 200
    assert response.json() == []


async def test_demo_get_robots_with_data(client, db_session):
    """GET /demo/robots 가 데이터 반환"""
    db_session.add(Robot(name="Demo1", model="m1", status="active", battery_level=70))
    await db_session.commit()

    del client.headers["X-API-Key"]
    response = await client.get("/demo/robots")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_demo_get_sensors(client):
    """키 없이 GET /demo/sensors"""
    del client.headers["X-API-Key"]
    response = await client.get("/demo/sensors?limit=5")
    assert response.status_code == 200


async def test_demo_stats(client):
    """키 없이 GET /demo/stats"""
    del client.headers["X-API-Key"]
    response = await client.get("/demo/stats")
    assert response.status_code == 200


# === 쓰기 차단 ===

async def test_demo_post_robot_not_allowed(client):
    """POST /demo/robots 는 제공되지 않음 — 쓰기는 /api/* + API Key 필요"""
    del client.headers["X-API-Key"]
    response = await client.post(
        "/demo/robots",
        json={"name": "X", "model": "v1", "status": "active", "battery_level": 50},
    )
    assert response.status_code in (404, 405)


async def test_demo_put_robot_not_allowed(client, db_session):
    """PUT /demo/robots/{id} 도 제공되지 않음 (로봇 실존해도 경로 자체 없음)"""
    db_session.add(Robot(name="R1", model="m", status="active", battery_level=50))
    await db_session.commit()

    del client.headers["X-API-Key"]
    response = await client.put(
        "/demo/robots/1",
        json={"status": "inactive", "battery_level": 30},
    )
    assert response.status_code in (404, 405)


async def test_demo_post_sensor_not_allowed(client):
    """POST /demo/sensors 도 제공되지 않음"""
    del client.headers["X-API-Key"]
    response = await client.post(
        "/demo/sensors",
        json={"robot_id": 1, "timestamp": "2026-01-01T00:00:00", "sensors": []},
    )
    assert response.status_code in (404, 405)


async def test_demo_does_not_expose_reset(client):
    """DELETE /demo/reset 도 제공되지 않음"""
    del client.headers["X-API-Key"]
    response = await client.delete("/demo/reset")
    assert response.status_code == 404


# === 회귀: /api/* 는 여전히 API Key 필수 ===

async def test_api_routes_still_require_key(client):
    del client.headers["X-API-Key"]
    response = await client.get("/api/robots")
    assert response.status_code == 401
    assert response.json()["error_code"] == "API_KEY_MISSING"


async def test_api_post_still_requires_key(client):
    del client.headers["X-API-Key"]
    response = await client.post(
        "/api/robots",
        json={"name": "X", "model": "v1", "status": "active", "battery_level": 50},
    )
    assert response.status_code == 401
