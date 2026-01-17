import requests
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"


def quick_mock():
    """빠른 테스트용 소량 데이터 생성"""

    # 1. 로봇 10대 생성 (이미 있으면 스킵)
    print("로봇 확인 중...")
    try:
        response = requests.get(f"{BASE_URL}/api/robots")
        if len(response.json()) >= 10:
            print("로봇 데이터 이미 있음 (스킵)")
        else:
            print("로봇 생성 중...")
            for i in range(1, 11):
                robot_data = {
                    "name": f"Robot-{i}",
                    "model": "Bot-V2",
                    "status": "active",
                    "battery_level": random.randint(70, 100)
                }
                requests.post(f"{BASE_URL}/api/robots", json=robot_data)
            print("로봇 10대 생성 완료")
    except:
        print("로봇 생성 실패 (서버 확인)")
        return

    # 2. 센서 데이터 100개만 생성 (빠름!)
    print("\n센서 데이터 100개 생성 중...")
    for i in range(100):
        robot_id = random.randint(1, 10)
        timestamp = datetime.now().isoformat()  # 현재 시간!

        payload = {
            "robot_id": robot_id,
            "timestamp": timestamp,
            "sensors": [
                {
                    "sensor_type": "IMU",
                    "data": {
                        "acceleration": {
                            "x": random.uniform(-2, 2),
                            "y": random.uniform(-2, 2),
                            "z": random.uniform(9, 10)
                        }
                    }
                },
                {
                    "sensor_type": "GPS",
                    "data": {
                        "latitude": random.uniform(37.4, 37.6),
                        "longitude": random.uniform(126.9, 127.1)
                    } if random.random() > 0.05 else None
                },
                {
                    "sensor_type": "LiDAR",
                    "data": {
                        "distance": random.uniform(0.5, 10.0),
                        "angle": random.uniform(0, 360)
                    }
                }
            ]
        }

        requests.post(f"{BASE_URL}/api/sensors", json=payload)

        if (i + 1) % 20 == 0:
            print(f"{i + 1}/100 완료")

    print("\n완료! 테스트 가능합니다.")


if __name__ == "__main__":
    quick_mock()