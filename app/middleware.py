import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.context import request_id

class RequestIDMiddleware(BaseHTTPMiddleware) :
    async def dispatch(self, request, call_next) :
        request_id.set(str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id.get()
        return response