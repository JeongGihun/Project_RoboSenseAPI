from enum import Enum

class SensorName(str, Enum) :
    IMU : "IMU"
    GPS : "GPS"
    LiDAR : "LiDAR"