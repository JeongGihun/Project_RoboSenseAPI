from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

class IMUData(BaseModel) :
    acceleration : Dict[str, float]
    gyroscope : Dict[str, float]

class SensorItem(BaseModel) :
    sensor_type : str
    data : IMUData | None

class SensorDataCreate(BaseModel) :
    robot_id : int
    timestamp : datetime
    sensors : List[SensorItem]

# pydantic으로 자동 타입 검증