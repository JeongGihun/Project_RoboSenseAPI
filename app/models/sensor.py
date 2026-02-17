from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from datetime import datetime

class IMUData(BaseModel) :
    acceleration : Dict[str, float]
    gyroscope : Dict[str, float]

class GPSData(BaseModel) :
    latitude : float
    longitude : float

class LiDARData(BaseModel) :
    distance : float
    angle : float

class SensorItem(BaseModel) :
    sensor_type : str
    data : Optional[Union[IMUData | GPSData | LiDARData]] = None

class SensorResponse(BaseModel) :
    id : int
    robot_id : int
    sensor_type : str
    timestamp : datetime
    raw_data : dict | None
    created_at : datetime

class SensorListResponse(BaseModel) :
    data : List[SensorResponse]
    next_cursor : Optional[int]
    has_more : bool

class SensorDataCreate(BaseModel) :
    robot_id : int
    timestamp : datetime
    sensors : List[SensorItem]

class FilteredSensorResponse(BaseModel) :
    robot_id : int
    sensor_type : str
    field : str
    original_data : Optional[List[float]] = None
    filtered_data : Optional[List[float]] = None
    window_size : int

# pydantic으로 자동 타입 검증
# 형식을 무조건 작성해야함. 전체를 List로 받는 경우는 가능