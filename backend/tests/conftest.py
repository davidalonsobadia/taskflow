"""Shared pytest fixtures for the backend test suite.

This is the first test harness in the repository. It boots the real FastAPI
app against an in-memory SQLite database and overrides the two request-scoped
dependencies tests care about:

* ``get_db`` -> a session bound to the throwaway SQLite engine.
* ``get_verified_user`` -> a seeded, verified user, so endpoints can be hit
  without minting JWTs.

The API-key middleware and Sentry are already disabled when ``TESTING=1`` (see
``app.main``), which the runner sets. We default the env here too so the suite
also works under a bare ``pytest`` invocation.
"""

import os

os.environ.setdefault("TESTING", "1")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import session as db_session_module
from app.db.base import Base
from app.db.session import get_db
from app.domains.auth.models import User
from app.domains.auth.utils import get_verified_user
from app.main import app

# Importing the models above (plus those pulled in transitively by ``app.main``)
# registers every table on ``Base.metadata`` so ``create_all`` builds the schema.


@pytest.fixture
def db_session():
    """A SQLAlchemy session on a fresh in-memory database, dropped after each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Rebind the app's SessionLocal (used by Celery tasks that open their own
    # session, e.g. tasks.generate_next_occurrence) to this throwaway engine, so
    # eager-mode tasks read and write the same in-memory database as the tests.
    original_bind = db_session_module.SessionLocal.kw.get("bind")
    db_session_module.SessionLocal.configure(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        db_session_module.SessionLocal.configure(bind=original_bind)
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def test_user(db_session) -> User:
    """A verified user that owns the data created in tests."""
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="not-a-real-hash",
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def client(db_session, test_user) -> TestClient:
    """A TestClient wired to the in-memory DB and authenticated as ``test_user``."""

    def override_get_db():
        yield db_session

    def override_get_verified_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_verified_user] = override_get_verified_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
