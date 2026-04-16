"""메트릭 엔드포인트 테스트 (D4 TDD RED)"""


async def test_metrics_returns_200(client):
    """/metrics → 200"""
    response = await client.get("/metrics")
    assert response.status_code == 200


async def test_metrics_has_required_fields(client):
    """/metrics 응답에 필수 필드 존재"""
    response = await client.get("/metrics")
    data = response.json()
    assert "request_count" in data
    assert "response_times" in data


async def test_metrics_response_times_has_percentiles(client):
    """response_times에 p50, p95, p99 포함"""
    response = await client.get("/metrics")
    data = response.json()
    rt = data["response_times"]
    assert "p50" in rt
    assert "p95" in rt
    assert "p99" in rt


async def test_metrics_no_auth_required(client):
    """/metrics는 API Key 없이 접근 가능"""
    response = await client.get("/metrics")
    assert response.status_code != 401
