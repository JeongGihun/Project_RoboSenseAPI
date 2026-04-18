"""커스텀 예외 핸들러 테스트 (D6 TDD RED)"""
import os


ADMIN_KEY = os.getenv("ADMIN_KEY", "test-admin-key")


async def _get_api_key(client) -> str:
    """테스트 헬퍼: API Key 발급"""
    resp = await client.post(
        "/admin/api-keys",
        json={"robot_id": None},
        headers={"X-Admin-Key": ADMIN_KEY}
    )
    return resp.json()["api_key"]


async def test_robot_not_found_error_format(client):
    """로봇 404 → 통일 에러 포맷"""
    api_key = await _get_api_key(client)
    response = await client.get(
        "/api/robots/99999",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data
    assert data["error_code"] == "ROBOT_NOT_FOUND"
    assert "message" in data
    assert "timestamp" in data


async def test_sensor_not_found_error_format(client):
    """센서 404 → 통일 에러 포맷"""
    api_key = await _get_api_key(client)
    response = await client.get(
        "/api/sensors/99999",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data
    assert data["error_code"] == "SENSOR_NOT_FOUND"
    assert "message" in data
    assert "timestamp" in data


async def test_api_key_missing_error_format(client):
    """API Key 누락 → 통일 에러 포맷"""
    response = await client.get("/api/robots", headers={"X-API-Key": ""})
    assert response.status_code == 401
    data = response.json()
    assert "error_code" in data
    assert data["error_code"] == "API_KEY_MISSING"
    assert "message" in data
    assert "timestamp" in data


async def test_api_key_invalid_error_format(client):
    """잘못된 API Key → 통일 에러 포맷"""
    response = await client.get(
        "/api/robots",
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 401
    data = response.json()
    assert "error_code" in data
    assert data["error_code"] == "API_KEY_INVALID"
    assert "message" in data
    assert "timestamp" in data


async def test_validation_error_format(client):
    """Pydantic 검증 실패 → 통일 에러 포맷"""
    api_key = await _get_api_key(client)
    response = await client.post(
        "/api/robots",
        json={"battery_level": 150},  # name 누락 + 범위 초과
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 422
    data = response.json()
    assert "error_code" in data
    assert "timestamp" in data
