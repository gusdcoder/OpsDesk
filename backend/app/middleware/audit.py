from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
from datetime import datetime

logger = structlog.get_logger()

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = datetime.now()
        method = request.method
        path = request.url.path
        ip_address = request.client.host if request.client else "unknown"
        
        response = await call_next(request)
        
        # Log response
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        status_code = response.status_code
        
        # Only log non-trivial endpoints
        if not path.startswith("/healthz") and not path.startswith("/readyz"):
            logger.info(
                "http_request",
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                ip_address=ip_address
            )
        
        return response
