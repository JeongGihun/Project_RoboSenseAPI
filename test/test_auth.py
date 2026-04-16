"""API Key 인증 테스트 (D3)"""
import os


ADMIN_KEY = os.getenv("ADMIN_KEY", "test-admin-key")


# === 인증 없이 보호 엔드포인트 접근 ===

async def test_robots_without_api_key_returns_401(client):
    """API Key 없이 /api/robots 접근 → 401"""
    response = await client.get("/api/robots", headers={"X-API-Key": ""})
    assert response.status_code == 401


async def test_sensors_without_api_key_returns_401(client):
    """API Key 없이 /api/sensors 접근 → 401"""
    response = await client.get("/api/sensors", headers={"X-API-Key": ""})
    assert response.status_code == 401


async def test_stats_without_api_key_returns_401(client):
    """API Key 없이 /api/stats 접근 → 401"""
    response = await client.get("/api/stats", headers={"X-API-Key": ""})
    assert response.status_code == 401


# === 무효한 키 ===

async def test_invalid_api_key_returns_401(client):
    """잘못된 API Key → 401"""
    response = await client.get(
        "/api/robots",
        headers={"X-API-Key": "invalid-garbage-key"}
    )
    assert response.status_code == 401


# === 유효한 키 ===

async def test_valid_api_key_returns_200(client):
    """유효한 API Key로 접근 → 200 (client fixture가 자동 발급)"""
    response = await client.get("/api/robots")
    assert response.status_code == 200


# === 폐기된 키 ===

async def test_revoked_key_returns_401(client):
    """폐기된 API Key → 401"""
    # 새 키 발급
    issue_resp = await client.post(
        "/admin/api-keys",
        json={"robot_id": None},
        headers={"X-Admin-Key": ADMIN_KEY}
    )
    api_key = issue_resp.json()["api_key"]
    key_id = issue_resp.json()["id"]

    # 폐기
    await client.delete(
        f"/admin/api-keys/{key_id}",
        headers={"X-Admin-Key": ADMIN_KEY}
    )

    # 폐기된 키로 접근
    response = await client.get(
        "/api/robots",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 401


# === /health는 인증 불필요 ===

async def test_health_no_auth_required(client):
    """GET /health_check는 API Key 없이 접근 가능"""
    response = await client.get("/health_check", headers={"X-API-Key": ""})
    assert response.status_code != 401
