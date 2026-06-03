from celery import Celery
from app.core.config import settings
import os
import sentry_sdk

# Initialize Sentry for Celery worker (if configured and not testing)
if settings.SENTRY_DSN and os.environ.get("TESTING") != "1":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        send_default_pii=True,
        traces_sample_rate=getattr(settings, "SENTRY_TRACES_SAMPLE_RATE", 0.0),
        profiles_sample_rate=getattr(settings, "SENTRY_PROFILES_SAMPLE_RATE", 0.0),
    )


# Configure Celery based on environment
if os.environ.get("TESTING") == "1":
    # Use eager mode for testing - tasks execute synchronously without Redis
    celery = Celery("taskflow-celery", broker="memory://")
    celery.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        broker_connection_retry_on_startup=False,
    )
else:
    # Normal mode for production
    celery = Celery("taskflow-celery", broker=settings.REDIS_URL)

# Auto-discover tasks in domain modules
# Add task modules here as you create them
celery.autodiscover_tasks(["app.domains.auth.tasks"])