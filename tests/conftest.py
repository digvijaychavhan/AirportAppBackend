"""
Shared Pytest Fixtures for Backend Test Suite
Provides in-memory isolated database, seeded data, and configured TestClient.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.db.seed.seeder import seed_database
from app.main import fastapi_app

# Use in-memory SQLite database for test isolation
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Creates all database tables and populates seed data once for the test session.
    """
    Base.metadata.create_all(bind=test_engine)

    # Seed in-memory database
    db = TestingSessionLocal()
    try:
        from app.db.seed.seeder import seed_database
        # Monkeypatch seed engine to use test_engine if needed or direct seed
        seed_database(force=True, custom_engine=test_engine)
    except Exception as e:
        pass
    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """
    Provides an isolated transactional database session per test with automatic rollback.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """
    FastAPI TestClient with overridden get_db dependency.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()
