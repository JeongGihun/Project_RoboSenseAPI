"""BFF demo 프록시 라우트 테스트.

랜딩페이지 JS가 키 없이 호출하는 경로. 서버가 내부에서 API Key 없이도 통과시킴.
"""
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.db_models import Robot


async def _client_without_key():
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_demo_get_robots_empty(client):
    """키 없이 GET /demo/robots 호출 가능 (빈 리스트)"""
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
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Demo1"


async def test_demo_post_robot(client):
    """키 없이 POST /demo/robots 로 로봇 생성 가능"""
    del client.headers["X-API-Key"]
    response = await client.post(
        "/demo/robots",
        json={"name": "NewBot", "model": "v1", "status": "active", "battery_level": 90},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "NewBot"


async def test_demo_get_sensors(client):
    """키 없이 GET /demo/sensors"""
    del client.headers["X-API-Key"]
    response = await client.get("/demo/sensors?limit=5")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "next_cursor" in body


async def test_demo_stats(client):
    """키 없이 GET /demo/stats"""
    del client.headers["X-API-Key"]
    response = await client.get("/demo/stats")
    assert response.status_code == 200


async def test_api_routes_still_require_key(client):
    """회귀: /api/* 는 여전히 API Key 필수 (BFF 추가해도 기존 보호 유지)"""
    del client.headers["X-API-Key"]
    response = await client.get("/api/robots")
    assert response.status_code == 401
    assert response.json()["error_code"] == "API_KEY_MISSING"


async def test_demo_does_not_expose_reset(client):
    """DELETE /demo/reset 은 제공되지 않음 (데이터 초기화는 admin 키로만)"""
    del client.headers["X-API-Key"]
    response = await client.delete("/demo/reset")
    assert response.status_code == 404
