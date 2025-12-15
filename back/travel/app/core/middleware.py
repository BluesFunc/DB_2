from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.utils.logging_util import log_operation, map_http_method_to_action
from jose import jwt, JWTError
import logging
import json

logger = logging.getLogger(__name__)

class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            
            # Log the request
            await self._log_request(request, response.status_code)
            
            if response.status_code >= 400:
                return self.handle_error(response)
            return response
        except HTTPException as exc:
            await self._log_request(request, exc.status_code)
            return self.handle_http_exception(exc)
        except Exception as exc:
            logger.error(f"Unhandled exception: {exc}")
            await self._log_request(request, 500, details={"error": str(exc)})
            return self.handle_unexpected_exception(exc)

    async def _log_request(self, request: Request, status_code: int, details: dict = None):
        """Log HTTP request to audit trail"""
        try:
            # Extract user ID from JWT token if present
            user_id = None
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
                try:
                    from app.core.config import settings
                    decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
                    user_id = decoded.get("sub")
                except:
                    pass
            
            # Extract resource info from path
            path_parts = request.url.path.split('/')
            resource_type = 'unknown'
            resource_id = None
            
            if len(path_parts) >= 4:
                resource_type = path_parts[3] if path_parts[3] else 'unknown'
                if len(path_parts) >= 5 and path_parts[4].isdigit():
                    resource_id = int(path_parts[4])
            
            # Get client IP
            ip_address = None
            if request.client:
                ip_address = request.client.host
            
            # Log the operation
            await log_operation(
                user_id=user_id,
                action=map_http_method_to_action(request.method),
                resource_type=resource_type,
                resource_id=resource_id,
                method=request.method,
                status_code=status_code,
                details_json=details,
                ip_address=ip_address
            )
        except Exception as e:
            logger.error(f"Error logging request: {e}", exc_info=True)

    def handle_error(self, response):
        return JSONResponse(
            status_code=response.status_code,
            content={"detail": getattr(response, 'body', b'').decode() if hasattr(response, 'body') else str(response)},
        )

    def handle_http_exception(self, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    def handle_unexpected_exception(self, exc):
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred."},
        )