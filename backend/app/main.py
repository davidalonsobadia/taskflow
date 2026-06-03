from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware

import sentry_sdk
from app.api.router import router
from app.core.config import settings
import os

from app.core.events.events import event_bus
from app.core.middleware.api_key import APIKeyMiddleware

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.domains.api_clients.api_key_loader import load_active_hashed_keys

from app import logger

# Middleware to prevent caching of API responses
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        # Only add no-cache headers for API endpoints
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


app = FastAPI(
    title="TaskFlow API",
    description="A simple FastAPI starter template with auth, users, and lists",
    version="1.0.0"
)

logger.info("Initializing TaskFlow FastAPI application...")

# Add no-cache middleware first (executes last in response chain)
app.add_middleware(NoCacheMiddleware)

# Configure CORS using settings
logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

def get_hashed_keys() -> set[str]:
    db: Session = SessionLocal()
    try:
        return load_active_hashed_keys(db)
    finally:
        db.close()

# Skip API key middleware in testing environment
is_testing = os.environ.get("TESTING") == "1"
if not is_testing:
    allowed_api_keys = get_hashed_keys()
    app.add_middleware(APIKeyMiddleware, allowed_keys=allowed_api_keys)

app.include_router(router)
# Initialize Sentry conditionally based on environment settings
if settings.SENTRY_DSN and not is_testing:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        send_default_pii=True,
        traces_sample_rate=getattr(settings, "SENTRY_TRACES_SAMPLE_RATE", 0.1),
        profiles_sample_rate=getattr(settings, "SENTRY_PROFILES_SAMPLE_RATE", 0.1),
    )
