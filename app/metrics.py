import threading
from collections import deque


_lock = threading.Lock()
_request_count = 0
_response_times = deque(maxlen=1000)


def record_request(duration_ms: float) -> None:
    """요청 처리 시간 기록."""
    global _request_count
    with _lock:
        _request_count += 1
        _response_times.append(duration_ms)


def get_metrics() -> dict:
    """현재 메트릭 반환."""
    with _lock:
        times = sorted(_response_times)
        count = len(times)
        if count == 0:
            percentiles = {"p50": 0, "p95": 0, "p99": 0}
        else:
            percentiles = {
                "p50": times[int(count * 0.5)],
                "p95": times[min(int(count * 0.95), count - 1)],
                "p99": times[min(int(count * 0.99), count - 1)],
            }
        return {
            "request_count": _request_count,
            "response_times": percentiles,
        }
