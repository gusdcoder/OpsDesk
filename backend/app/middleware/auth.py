from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt
import structlog

from app.config import settings
from app.utils.auth_utils import decode_token

logger = structlog.get_logger()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        user_info = None
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = decode_token(token)
            if payload:
                user_info = payload
                request.state.user_id = payload.get("sub")
                request.state.user_role = payload.get("role")
        
        # Store in request state for use in handlers
        if not hasattr(request.state, 'user_id'):
            request.state.user_id = None
            request.state.user_role = None
        
        response = await call_next(request)
        return response
