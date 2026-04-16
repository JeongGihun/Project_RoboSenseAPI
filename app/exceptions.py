from datetime import datetime, timezone


class BaseAPIException(Exception):
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "서버 내부 오류"

    def __init__(self, detail: dict | None = None):
        self.detail = detail or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()


class RobotNotFoundError(BaseAPIException):
    status_code = 404
    error_code = "ROBOT_NOT_FOUND"
    message = "해당 로봇이 존재하지 않습니다"


class SensorNotFoundError(BaseAPIException):
    status_code = 404
    error_code = "SENSOR_NOT_FOUND"
    message = "해당 센서 데이터가 존재하지 않습니다"


class SensorTypeInvalidError(BaseAPIException):
    status_code = 400
    error_code = "SENSOR_TYPE_INVALID"
    message = "지원하지 않는 센서 타입입니다"


class ApiKeyMissingError(BaseAPIException):
    status_code = 401
    error_code = "API_KEY_MISSING"
    message = "API 키가 필요합니다"


class ApiKeyInvalidError(BaseAPIException):
    status_code = 401
    error_code = "API_KEY_INVALID"
    message = "유효하지 않은 API 키입니다"
