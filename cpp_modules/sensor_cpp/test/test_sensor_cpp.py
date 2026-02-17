import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

import sensor_cpp

class MockIMU :
    def __init__(self):
        self.acceleration = {"x" : 1.0, "y" : 2.0, "z" : 9.8}
        self.gyroscope = {"x" : 0.1, "y" : 0.2, "z" : 0.3}

class MockGPS :
    def __init__(self):
        self.latitude = 39.2
        self.longitude = 127.0

class MockLiDAR :
    def __init__(self):
        self.distance = 6.5
        self.angle = 40.0

def test_serialize_imu_data() :
    mock_imu = MockIMU()
    result = sensor_cpp.serialize_imu_data(mock_imu)

    assert result["acceleration"]["x"] == 1.0
    assert result["acceleration"]["y"] == 2.0
    assert result["acceleration"]["z"] == 9.8
    assert result["gyroscope"]["x"] == 0.1
    assert result["gyroscope"]["y"] == 0.2
    assert result["gyroscope"]["z"] == 0.3

def test_serialize_gps_data() :
    mock_gps = MockGPS()
    result = sensor_cpp.serialize_gps_data(mock_gps)

    assert result["latitude"] == 39.2
    assert result["longitude"] == 127.0

def test_serialize_lidar_data() :
    mock_lidar = MockLiDAR()
    result = sensor_cpp.serialize_lidar_data(mock_lidar)

    assert result["distance"] == 6.5
    assert result["angle"] == 40.0

def test_add() :
    result = sensor_cpp.add(2, 3)
    assert result == 5

def test_moving_average_basic() :
    result = sensor_cpp.moving_average([1.0, 2.0, 3.0, 4.0, 5.0], 3)
    assert result == [2.0, 3.0, 4.0]

def test_moving_average_window_too_large() :
    result = sensor_cpp.moving_average([1.0, 2.0], 3)
    assert result == []