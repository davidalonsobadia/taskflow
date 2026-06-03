from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib

EXEMPT_PATHS = [
    "/api/v1/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/v1/psp/mollie/webhooks/payment"  # Mollie webhook - uses signature validation
]

class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_keys: set[str]):
        super().__init__(app)
        self.allowed_keys = allowed_keys

    async def dispatch(self, request: Request, call_next):
        # Skip OPTIONS requests (preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Allow exempt paths without requiring an API key
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)
        
        raw_key = request.headers.get("x-api-key")
        if not raw_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing API key"}
            )

        hashed = hashlib.sha256(raw_key.encode()).hexdigest()
        if hashed not in self.allowed_keys:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid API key"}
            )

        return await call_next(request)
