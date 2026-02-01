# test_put.py 만들어서 실행
import requests

# 1. 로봇 1번 현재 상태 확인
response = requests.get("http://localhost/api/robots/1")
print("변경 전:", response.json())

# 2. PUT으로 상태 변경
response = requests.put(
    "http://localhost/api/robots/1",
    json={
        "status": "maintenance",
        "battery_level": 50
    }
)
print("PUT 응답:", response.status_code, response.text)

# 3. 다시 확인
response = requests.get("http://localhost/api/robots/1")
print("변경 후:", response.json())