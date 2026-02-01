from locust import HttpUser, task, constant
import random
import uuid
from datetime import datetime, timedelta

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

class User(HttpUser) :
    host = "http://localhost"
    wait_time = constant(0)

    @task(40)
    def post_sensor_data(self):
        """센서 데이터 수집"""
        robot_id = random.randint(1, 10)
        timestamp = datetime.now().isoformat()
        payload = generate_sensor_payload(robot_id, timestamp)

        self.client.post("/api/sensors", json = payload)

    @task(5)
    def update_robot_status(self):
        """로봇 상태 업데이트"""
        robot_id = random.randint(1, 10)
        update_data = {
            "status" : random.choice(["active", "inactive", "maintenance"]),
            "battery_level" : random.randint(20, 100)
        }
        self.client.put(f"/api/robots/{robot_id}", json = update_data)

    @task(3)
    def get_all_robots(self):
        """전체 로봇 조회"""
        self.client.get("/api/robots")

    @task(3)
    def get_robot_status(self):
        """특정 로봇 조회"""
        robot_id = random.randint(1, 10)
        self.client.get(f"/api/robots/{robot_id}")

    @task(1)
    def get_sensors_by_robot(self):
        """로봇 ID로 필터링 시"""
        robot_id = random.randint(1, 10)
        self.client.get(f"/api/sensors?robot_id={robot_id}")

    @task(1)
    def get_sensors_by_type(self):
        """센서 타입으로 필터링 시"""
        sensor_type = random.choice(["IMU", "GPS", "LiDAR"])
        self.client.get(f"/api/sensors?sensor_type={sensor_type}")

    # @task(1)
    # def register_robot(self):
    #     """로봇 등록"""
    #     robot_data = {
    #         "name" : f"Robot-Locust-{uuid.uuid4().hex[:8]}",
    #         "model" : "Bot-V2",
    #         "status" : "active",
    #         "battery_level" : random.randint(70, 100)
    #     }
    #     self.client.post("/api/robots", json = robot_data)

    @task(1)
    def get_stats(self):
        """센서 데이터 통계"""
        self.client.get("/api/stats")
    # 시간 별 기능은 만들었으나, 우선 디폴트만 테스트


    # @task(50)
    # def ping(self):
    #     self.client.get("/health_check")