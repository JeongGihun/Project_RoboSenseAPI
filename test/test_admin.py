"""관리자 API Key 관리 테스트 (D3 TDD RED)"""
import os


ADMIN_KEY = os.getenv("ADMIN_KEY", "test-admin-key")


# === POST /admin/api-keys ===

async def test_issue_api_key_success(client):
    """API Key 발급 성공"""
    response = await client.post(
        "/admin/api-keys",
        json={"robot_id": None},
        headers={"X-Admin-Key": ADMIN_KEY}
    )
    assert response.status_code == 201
    data = response.json()
    assert "api_key" in data
    assert "id" in data
    assert len(data["api_key"]) > 20  # 충분한 길이


async def test_issue_api_key_without_admin_key(client):
    """ADMIN_KEY 없이 발급 → 401"""
    response = await client.post(
        "/admin/api-keys",
        json={"robot_id": None}
    )
    assert response.status_code == 401


async def test_issue_api_key_wrong_admin_key(client):
    """잘못된 ADMIN_KEY → 401"""
    response = await client.post(
        "/admin/api-keys",
        json={"robot_id": None},
        headers={"X-Admin-Key": "wrong-admin-key"}
    )
    assert response.status_code == 401


# === GET /admin/api-keys ===

async def test_list_api_keys(client):
    """API Key 목록 조회"""
    # 키 하나 발급
    await client.post(
        "/admin/api-keys",
        json={"robot_id": None},
        headers={"X-Admin-Key": ADMIN_KEY}
    )

    response = await client.get(
        "/admin/api-keys",
        headers={"X-Admin-Key": ADMIN_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    # 해시는 반환하지 않아야 함
    assert "key_hash" not in data[0]
    assert "salt" not in data[0]


# === DELETE /admin/api-keys/{id} ===

async def test_revoke_api_key(client):
    """API Key 폐기"""
    # 발급
    issue_resp = await client.post(
        "/admin/api-keys",
        json={"robot_id": None},
        headers={"X-Admin-Key": ADMIN_KEY}
    )
    key_id = issue_resp.json()["id"]

    # 폐기
    response = await client.delete(
        f"/admin/api-keys/{key_id}",
        headers={"X-Admin-Key": ADMIN_KEY}
    )
    assert response.status_code == 200


# === 발급된 키로 보호 엔드포인트 접근 ===

async def test_issued_key_works(client):
    """발급된 키로 보호 엔드포인트 접근 가능"""
    issue_resp = await client.post(
        "/admin/api-keys",
        json={"robot_id": None},
        headers={"X-Admin-Key": ADMIN_KEY}
    )
    api_key = issue_resp.json()["api_key"]

    response = await client.get(
        "/api/robots",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200


async def test_list_api_keys_without_admin_key(client):
    """ADMIN_KEY 없이 목록 조회 → 401"""
    response = await client.get("/admin/api-keys")
    assert response.status_code == 401


async def test_revoke_nonexistent_key(client):
    """존재하지 않는 키 폐기"""
    response = await client.delete(
        "/admin/api-keys/99999",
        headers={"X-Admin-Key": ADMIN_KEY}
    )
    assert response.status_code == 200


async def test_issue_key_with_robot_id(client, db_session):
    """robot_id 지정하여 키 발급"""
    from app.models.db_models import Robot
    robot = Robot(name="Bot", model="v1", status="active", battery_level=80)
    db_session.add(robot)
    await db_session.commit()

    response = await client.post(
        "/admin/api-keys",
        json={"robot_id": robot.id},
        headers={"X-Admin-Key": ADMIN_KEY}
    )
    assert response.status_code == 201
    assert response.json()["robot_id"] == robot.id
