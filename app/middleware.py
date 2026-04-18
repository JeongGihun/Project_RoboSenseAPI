import uuid
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from app.context import request_id
from app.metrics import record_request

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id.set(str(uuid.uuid4()))
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        record_request(duration_ms)
        response.headers["X-Request-ID"] = request_id.get()

        logger.info(
            "request completed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response