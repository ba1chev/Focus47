import hmac
import secrets
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.constants import (
    CSRF_COOKIE_NAME, CSRF_HEADER_NAME, SAFE_METHODS, CSRF_EXEMPT_PATHS
)


class CSRFMiddleware(BaseHTTPMiddleware):
    """Double-submit-cookie CSRF protection.

    A random token lives in a non-HttpOnly cookie so the SPA can read it and
    echo it back in the X-CSRF-Token header. On unsafe methods the header must
    match the cookie (constant-time compare) or the request is rejected with
    403 — an attacker's cross-site form can send the cookie but cannot read it
    to set the header. Login/register are exempt: no session exists to protect
    yet and the client has no token on its first visit."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)

        if request.method not in SAFE_METHODS and request.url.path not in CSRF_EXEMPT_PATHS:
            header_token = request.headers.get(CSRF_HEADER_NAME)
            if (
                not cookie_token
                or not header_token
                or not hmac.compare_digest(cookie_token, header_token)
            ):
                return JSONResponse(
                    status_code=403, content={"detail": "CSRF token missing or invalid"}
                )

        response = await call_next(request)

        if not cookie_token:
            response.set_cookie(
                key=CSRF_COOKIE_NAME,
                value=secrets.token_urlsafe(32),
                httponly=False,
                samesite="strict"
            )
        return response
