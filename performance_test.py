"""
각 엔드포인트별 응답 시간 측정 스크립트
"""
import requests
import time
from datetime import datetime
import statistics

BASE_URL = "http://localhost:80"


def measure_endpoint(name, method, url, json_data=None, params=None, iterations=10):
    """엔드포인트 성능 측정"""
    print(f"\n{'=' * 60}")
    print(f"📊 {name}")
    print(f"{'=' * 60}")

    times = []
    success_count = 0
    fail_count = 0

    for i in range(iterations):
        try:
            start = time.time()

            if method == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=json_data, timeout=10)

            elapsed = (time.time() - start) * 1000  # ms로 변환

            if 200 <= response.status_code < 300:
                times.append(elapsed)
                success_count += 1
                print(f"  ✓ {i + 1}번째: {elapsed:.2f}ms (status: {response.status_code})")
            else:
                fail_count += 1
                print(f"  ✗ {i + 1}번째: 실패 (status: {response.status_code})")

        except Exception as e:
            fail_count += 1
            print(f"  ✗ {i + 1}번째: 에러 - {str(e)}")

    # 통계 출력
    if times:
        print(f"\n📈 통계:")
        print(f"  - 성공: {success_count}/{iterations}")
        print(f"  - 평균: {statistics.mean(times):.2f}ms")
        print(f"  - 최소: {min(times):.2f}ms")
        print(f"  - 최대: {max(times):.2f}ms")
        print(f"  - 중앙값: {statistics.median(times):.2f}ms")
        if len(times) > 1:
            print(f"  - 표준편차: {statistics.stdev(times):.2f}ms")
    else:
        print(f"\n❌ 모든 요청 실패 ({fail_count}/{iterations})")

    return times


def main():
    print("=" * 60)
    print("🚀 API 성능 측정 시작")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/health_check", timeout=2)
        if response.status_code == 200:
            print("✓ 서버 연결 확인 완료\n")
        else:
            print("✗ 서버 응답 이상")
            return
    except Exception as e:
        print(f"✗ 서버 연결 실패: {e}")
        return

    results = {}

    # 1. POST /api/sensors (센서 데이터 수집)
    sensor_payload = {
        "robot_id": 1,
        "timestamp": datetime.now().isoformat(),
        "sensors": [
            {
                "sensor_type": "IMU",
                "data": {
                    "acceleration": {"x": 1.2, "y": -0.5, "z": 9.8},
                    "gyroscope": {"x": 0.1, "y": 0.2, "z": 0.3}
                }
            },
            {
                "sensor_type": "GPS",
                "data": {
                    "latitude": 37.5665,
                    "longitude": 126.9780
                }
            },
            {
                "sensor_type": "LiDAR",
                "data": {
                    "distance": 3.5,
                    "angle": 45
                }
            }
        ]
    }
    results['POST /api/sensors'] = measure_endpoint(
        "센서 데이터 수집",
        "POST",
        f"{BASE_URL}/api/sensors",
        json_data=sensor_payload
    )

    # 2. GET /api/robots (로봇 목록 조회)
    results['GET /api/robots'] = measure_endpoint(
        "로봇 목록 조회",
        "GET",
        f"{BASE_URL}/api/robots"
    )

    # 3. GET /api/robots?status=active (상태별 필터링)
    results['GET /api/robots?status=active'] = measure_endpoint(
        "로봇 목록 조회 (상태 필터)",
        "GET",
        f"{BASE_URL}/api/robots",
        params={"status": "active"}
    )

    # 4. GET /api/robots/{id} (특정 로봇 상세)
    results['GET /api/robots/1'] = measure_endpoint(
        "특정 로봇 상세 조회",
        "GET",
        f"{BASE_URL}/api/robots/1"
    )

    # 5. GET /api/sensors (센서 데이터 조회)
    results['GET /api/sensors'] = measure_endpoint(
        "센서 데이터 조회 (기본 100개)",
        "GET",
        f"{BASE_URL}/api/sensors"
    )

    # 6. GET /api/sensors?robot_id=1 (로봇별 필터)
    results['GET /api/sensors?robot_id=1'] = measure_endpoint(
        "센서 데이터 조회 (로봇별)",
        "GET",
        f"{BASE_URL}/api/sensors",
        params={"robot_id": 1}
    )

    # 7. GET /api/sensors?sensor_type=IMU (센서타입별 필터)
    results['GET /api/sensors?sensor_type=IMU'] = measure_endpoint(
        "센서 데이터 조회 (타입별)",
        "GET",
        f"{BASE_URL}/api/sensors",
        params={"sensor_type": "IMU"}
    )

    # 8. GET /api/stats (통계)
    results['GET /api/stats'] = measure_endpoint(
        "통계 조회",
        "GET",
        f"{BASE_URL}/api/stats"
    )

    # 최종 요약
    print("\n" + "=" * 60)
    print("📊 최종 요약")
    print("=" * 60)

    summary_data = []
    for endpoint, times in results.items():
        if times:
            avg = statistics.mean(times)
            summary_data.append((endpoint, avg))

    # 평균 응답 시간 기준 정렬
    summary_data.sort(key=lambda x: x[1])

    print("\n⚡ 빠른 순서:")
    for i, (endpoint, avg) in enumerate(summary_data, 1):
        print(f"  {i}. {endpoint:40s} {avg:>8.2f}ms")

    print("\n🐌 느린 엔드포인트 (50ms 이상):")
    slow_endpoints = [(e, t) for e, t in summary_data if t >= 50]
    if slow_endpoints:
        for endpoint, avg in slow_endpoints:
            print(f"  ⚠️  {endpoint:40s} {avg:>8.2f}ms")
    else:
        print("  없음 - 모든 엔드포인트가 50ms 이내!")

    print("\n" + "=" * 60)
    print(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()