from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.database import Base
from datetime import datetime, timezone

class SensorData(Base) :
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index = True)
    robot_id = Column(Integer, index = True)
    timestamp = Column(DateTime(timezone=True))
    sensors = Column(JSON)
    created_at = Column(DateTime(timezone=True), default = lambda:datetime.now(timezone.utc))