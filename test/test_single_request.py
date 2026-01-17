# 성능 확인용

import requests
import time

url = "http://localhost:8000/api/sensors"

data = {
    "robot_id": 1,
    "timestamp": "2024-01-04T10:30:00",
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

print("10번 연속 요청 시작...\n")

times = []
for i in range(10):
    start = time.time()
    response = requests.post(url, json=data)
    elapsed = (time.time() - start) * 1000
    times.append(elapsed)
    print(f"{i+1}번째 요청: {elapsed:.2f}ms (응답: {response.status_code})")

print(f"\n평균: {sum(times) / len(times):.2f}ms")
print(f"최소: {min(times):.2f}ms")
print(f"최대: {max(times):.2f}ms")