from collections import defaultdict, deque
from time import monotonic

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple per-instance sliding window. Enough for a public demo."""

    def __init__(self, app: ASGIApp, max_per_minute: int) -> None:
        super().__init__(app)
        self.max_per_minute = max_per_minute
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        if self.max_per_minute <= 0 or request.method in {"GET", "HEAD", "OPTIONS"}:
            return await call_next(request)
        if request.url.path in {"/health", "/"}:
            return await call_next(request)

        now = monotonic()
        ip = self._client_ip(request)
        window = self._hits[ip]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= self.max_per_minute:
            return JSONResponse(
                {"detail": "Rate limit exceeded. Try again in a minute."},
                status_code=429,
            )
        window.append(now)
        return await call_next(request)
