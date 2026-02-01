from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.models.enum import Status, SensorName

class SensorInRobot(BaseModel) :
    sensor_type : SensorName
    timestamp : datetime
    raw_data : dict | None

class RobotDetailResponse(BaseModel) :
    id: int
    name: str
    model: str
    status: Status
    battery_level: int = Field(ge=0, le=100)
    last_seen: datetime | None
    created_at: datetime
    recent_sensors : List[SensorInRobot] = []

class RobotCreate(BaseModel) :
    name : str
    model : str
    status : Status
    battery_level : int = Field(ge=0, le=100)

class RobotResponse(BaseModel) :
    id : int
    name : str
    model : str
    status : Status
    battery_level : int = Field(ge=0, le=100)
    last_seen : datetime | None
    created_at : datetime

class RobotStatusUpdate(BaseModel) :
    status : Status
    battery_level : int = Field(ge=0, le=100)