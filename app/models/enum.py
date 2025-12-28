from enum import Enum

class Status(str, Enum) :
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"

class SensorName(str, Enum) :
    IMU = "IMU"
    GPS = "GPS"
    LiDAR = "LiDAR"