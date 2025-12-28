from sqlalchemy import Column, Integer, String, DateTime, JSON, CheckConstraint, Enum, ForeignKey
from app.database import Base
from datetime import datetime, timezone
from app.models.enum import Status, SensorName
from sqlalchemy.orm import relationship

class Robot(Base) :
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, nullable=False)
    model = Column(String)
    status = Column(Enum(Status), default = Status.active)
    battery_level = Column(Integer, CheckConstraint('battery_level >= 0 AND battery_level <= 100'))
    last_seen = Column(DateTime(timezone=True), nullable = True)
    created_at = Column(DateTime(timezone=True), default = lambda:datetime.now(timezone.utc))

    sensor_data = relationship("SensorData", back_populates= "robot")

class SensorData(Base) :
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index = True)
    robot_id = Column(Integer, ForeignKey("robots.id"), index = True)
    sensor_type = Column(Enum(SensorName), nullable = False)
    timestamp = Column(DateTime(timezone=True))
    raw_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), default = lambda:datetime.now(timezone.utc))

    robot = relationship("Robot", back_populates="sensor_data")