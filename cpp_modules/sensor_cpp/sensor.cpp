#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <map>
#include <string>

namespace py = pybind11;

// 간단한 덧셈 함수
int add(int a, int b) {
    return a + b;
}

// IMU 데이터 직렬화
py::dict serialize_imu_data(py::object imu_obj) {
    py::dict result;

    // accelation 추출
    py::dict acc = imu_obj.attr("acceleration");
    py::dict acc_dict;
    acc_dict["x"] = acc["x"];
    acc_dict["y"] = acc["y"];
    acc_dict["z"] = acc["z"];
    result["acceleration"] = acc_dict;

    // gyroscope 추출
    if (py::hasattr(imu_obj, "gyroscope")) {
        py::dict gyro = imu_obj.attr("gyroscope");
        py::dict gyro_dict;
        gyro_dict["x"] = gyro["x"];
        gyro_dict["y"] = gyro["y"];
        gyro_dict["z"] = gyro["z"];
        result["gyroscope"] = gyro_dict;
    }

    return result;
}

// gps 직렬화
py::dict serialize_gps_data(py::object gps_obj) {
    py::dict result;
    result["latitude"] = gps_obj.attr("latitude");
    result["longitude"] = gps_obj.attr("longitude");
    return result;
}

// lidar 직렬화
py::dict serialize_lidar_data(py::object lidar_obj) {
    py::dict result;
    result["distance"] = lidar_obj.attr("distance");
    result["angle"] = lidar_obj.attr("angle");
    return result;
}

// 통합
py::object serialize_sensor_data(py::object sensor_data, const std::string& sensor_type) {

    if (sensor_data.is_none()) {
        return py::none();
    }

    if (sensor_type == "IMU") {
        return serialize_imu_data(sensor_data);
    } else if (sensor_type == "GPS") {
        return serialize_gps_data(sensor_data);
    } else if (sensor_type == "LiDAR") {
        return serialize_lidar_data(sensor_data);
    }

    return py::none();
}

py::dict calculate_null_rates(py::list stats_data) {
    py::dict result;

    for (auto item : stats_data) {
        py::tuple row = item.cast<py::tuple>();

        // sensor_type, total, null 언팩
        py::object sensor_type_obj = row[0];
        int total = row[1].cast<int>();
        int null_count = row[2].cast<int>();

        // sensor_type.value 추출
        std::string sensor_type = sensor_type_obj.attr("value").cast<std::string>();

        double null_rate = 0.0;
        if (total > 0) {
            null_rate = std::round((double)null_count / total * 100.0) / 100.0;
        }

        result[sensor_type.c_str()] = null_rate;
    }

    return result;
}

py::dict calculate_robot_summary(py::list robots_stats) {
    py::dict status_counts;
    int total = 0;

    for (auto item : robots_stats) {
        py::tuple row = item.cast<py::tuple>();

        py::object status_obj = row[0];
        int count = row[1].cast<int>();

        std::string status = status_obj.attr("value").cast<std::string>();

        status_counts[status.c_str()] = count;
        total += count;
    }

    py::dict result;
    result["total_robot"] = total;
    result["active"] = status_counts.contains("active") ? status_counts["active"].cast<int>() : 0;
    result["inactive"] = status_counts.contains("inactive") ? status_counts["inactive"].cast<int>() : 0;

    return result;
}

// 바인딩
PYBIND11_MODULE(sensor_cpp, m) {
    m.doc() = "C++ sensor data serialization module";

    // test
    m.def("add", &add, "Test Add two number");

    // 직렬화 함수
    m.def("serialize_sensor_data", &serialize_sensor_data,
        "Serialize sensor data to dict",
        py::arg("sensor_data"),
        py::arg("sensor_type"));

    m.def("serialize_imu_data", &serialize_imu_data,
        "Serialize IMU data");

    m.def("serialize_gps_data", &serialize_gps_data,
        "Serialize GPS data");

    m.def("serialize_lidar_data", &serialize_lidar_data,
        "Serialize LiDAR data");

    m.def("calculate_null_rates", &calculate_null_rates,
        "Calculate null rates from sensor stats",
        py::arg("stats_data"));

    m.def("calculate_robot_summary", &calculate_robot_summary,
        "Calculate robot status summary",
        py::arg("robot_stats"));
}