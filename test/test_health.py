"""헬스체크 테스트 (D4 TDD RED)"""


async def test_health_returns_200(client):
    """정상 상태에서 /health → 200"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


async def test_health_check_backward_compat(client):
    """기존 /health_check 경로도 동작"""
    response = await client.get("/health_check")
    # 401이 아닌 것만 확인 (DB/Redis 상태에 따라 200 또는 503)
    assert response.status_code in (200, 503)


async def test_health_has_db_redis_fields(client):
    """/health 응답에 db, redis 필드 존재"""
    response = await client.get("/health")
    data = response.json()
    assert "db" in data
    assert "redis" in data


async def test_health_no_auth_required(client):
    """/health는 API Key 없이 접근 가능"""
    response = await client.get("/health")
    assert response.status_code != 401
