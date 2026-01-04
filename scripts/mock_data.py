import requests
import random
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000"
TOTAL_ROBOT = 10
TOTAL_REQUESTS = 50000

def create_robot() :
    """로봇 10대 생성"""
    print("로봇 생성")

    for i in range(1, 11) :
        robot_data = {
            "name" : f"Robot-{i}",
            "model" : "Bot-V2",
            "status" : "active",
            "battery_level" : random.randint(70, 100)
        }

        response = requests.post(
            f"{BASE_URL}/api/robots",
            json = robot_data
        )

        if response.status_code == 201 :
            print(f"Robot-{i} 생성 완료")
        else :
            print(f"Robot-{i} 생성 실패 : {response.text}")

def generate_sensor_payload(robot_id, timestamp) :
    """페이로드 생성"""

    imu_data = {
        "sensor_type" : "IMU",
        "data" : {
            "acceleration" : {
                "x" : random.uniform(-2, 2),
                "y" : random.uniform(-2, 2),
                "z" : random.uniform(9, 10)
            },
            "gyroscope" : {
                "x" : random.uniform(-1, 1),
                "y" : random.uniform(-1, 1),
                "z" : random.uniform(-1, 1)
            }
        }
    }

    if random.random() < 0.05 :
        gps_data = {
            "sensor_type" : "GPS",
            "data" : None
        }
    else :
        gps_data = {
            "sensor_type": "GPS",
            "data": {
                "latitude" : random.uniform(37.4, 37.6),
                "longitude" : random.uniform(126.9, 127.1)
            }
        }

    lidar_data = {
        "sensor_type" : "LiDAR",
        "data" : {
            "distance" : random.uniform(0.5, 10.0),
            "angle" : random.uniform(0, 360)
        }
    }

    return {
        "robot_id" : robot_id,
        "timestamp" : timestamp,
        "sensors" : [imu_data, gps_data, lidar_data]
    }

def create_sensor_data() :
    """센서 데이터 50,000번 API 호출"""
    print("센서 데이터 생성 중")

    success_cnt = 0
    fail_cnt = 0
    start_time = time.time()

    for i in range(TOTAL_REQUESTS) :
        rdm_robot_id = random.randint(1, 10)
        now = datetime.now()
        rdm_timestamp = (now - timedelta(seconds=random.randint(0, 24 * 60 * 60))).isoformat()

        payload = generate_sensor_payload(rdm_robot_id, rdm_timestamp)

        for retry in range(3) :
            try :
                response = requests.post(
                    f"{BASE_URL}/api/sensors",
                    json=payload,
                    timeout=5
                )

                if 200 <= response.status_code < 300 :
                    success_cnt += 1
                    break
                else :
                    if retry == 2 :
                        fail_cnt += 1
                        print(f"{i+1}번 데이터 실패 : {response.status_code}")
            except Exception as e :
                if retry == 2 :
                    fail_cnt += 1
                    print(f"{i+1}번 데이터 실패 : {e}")
                else :
                    time.sleep(0.1)

        if (i+1) % 1000 == 0 :
            print(f"{(i+1)/TOTAL_REQUESTS*100:.1f}% 진행중")


    total_time = time.time() - start_time
    print("센서 데이터 생성 완료")
    print(f"총 : {TOTAL_REQUESTS}개, 성공 : {success_cnt}, 실패 : {fail_cnt}")
    print(f"총 {total_time/60:.1f}분 소요")


def main() :
    print("=" * 50)
    print("Mock Data Creating")
    print("=" * 50)

    create_robot()

    print("\n" + "=" * 50)

    create_sensor_data()

    print("=" * 50)
    print("Complete!")
    print("=" * 50)

if __name__ == "__main__" :
    try :
        response = requests.get(f"{BASE_URL}/health_check", timeout = 2)
        if 200 <= response.status_code < 300 :
            print("Check Server connection")
            main()
        else :
            print("Server Error")
    except Exception as e :
        print("Server not execution")
        print(f"\n에러 : {e}")