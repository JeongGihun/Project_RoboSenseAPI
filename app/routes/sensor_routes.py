from fastapi import APIRouter
from app.models.sensor import SensorDataCreate
from typing import Optional

router = APIRouter()

# 메모리 저장
db_tmp = []

#POST /api/sensors (센서 데이터 수집)
#GET /api/sensors (데이터 조회 + 필터링)

@router.post('/api/sensors')
async def collect_sensor_data(data : SensorDataCreate) :
    db_tmp.append(data.model_dump())
    return {"status" : "success", "inserted_count" : len(data.sensors), "robot_id" : data.robot_id}

@router.get('/api/sensors')
async def check_filter_data(robot_id : Optional[int] = None) :
    if robot_id :
        filtered = [row for row in db_tmp if row['robot_id']==robot_id]
        return filtered
    return db_tmp