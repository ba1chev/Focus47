from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.constants import SECURITY_HEADERS


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds baseline security response headers to every response."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        response = await call_next(request)
        for name, value in SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
        return response
