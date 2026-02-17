// sensor.h
#pragma once
#include <string>
#include <map>

// 순수 C++ 함수 (테스트 가능!)
std::map<std::string, double> extract_acceleration(
    const std::map<std::string, double>& acc
) {
    std::map<std::string, double> result;
    result["x"] = acc.at("x");
    result["y"] = acc.at("y");
    result["z"] = acc.at("z");
    return result;
}

double calculate_null_rate(int total, int null_count) {
    if (total == 0) return 0.0;
    return std::round((double)null_count / total * 100.0) / 100.0;
}