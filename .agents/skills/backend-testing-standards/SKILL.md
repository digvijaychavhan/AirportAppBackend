---
name: backend-testing-standards
description: Defines testing standards and patterns for the FastAPI backend.
metadata:
  version: "1.0"
  domain: "tests"
---

# Backend Testing Standards

This document establishes the testing standards and patterns for the FastAPI backend, transitioning from simple happy-path scripts to robust, isolated, and comprehensive test suites.

## 1. Test Architecture & Fixtures

Use `pytest` with a central `conftest.py` to manage shared fixtures. Do **NOT** mutate the live `app.db` database. Instead, use an in-memory SQLite database for strict test isolation.

### `conftest.py` Template

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import fastapi_app
from app.core.database import Base
from app.core.dependencies import get_db

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    # Override the dependency
    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as client:
        yield client
    
    # Clean up override
    fastapi_app.dependency_overrides.clear()
```

## 2. Test Categories & File Naming

Organize tests strictly by scope and domain:

- **Unit Tests**: Focus on service layer business logic.
  - Path: `tests/unit/test_<domain>_service.py`
  - Example: `tests/unit/test_flights_service.py`
- **Integration Tests**: Focus on API endpoint inputs, outputs, and routing.
  - Path: `tests/integration/test_<domain>_api.py`
  - Example: `tests/integration/test_wayfinding_api.py`
- **WebSocket Tests**: Focus on Socket.IO event signaling.
  - Path: `tests/integration/test_signaling.py`

## 3. Mandatory Negative Test Patterns

Do not just test 200 OK. You MUST include negative and validation test cases.

### 400 Bad Request
```python
def test_create_kiosk_malformed_payload(test_client):
    # Missing required 'location' field
    payload = {"status": "active"}
    response = test_client.post("/kiosks/", json=payload)
    assert response.status_code == 422 # FastAPI Pydantic default validation failure
```

### 404 Not Found
```python
def test_get_nonexistent_flight(test_client):
    response = test_client.get("/flights/INVALID_ID")
    assert response.status_code == 404
    assert response.json()["detail"] == "Flight not found"
```

### 422 Unprocessable Entity
```python
def test_invalid_boarding_pass(test_client):
    payload = {"mrz_string": "123"} # Too short
    response = test_client.post("/flights/decode-boarding-pass", json=payload)
    assert response.status_code == 422
```

## 4. Unit Test Patterns for Key Services

Test business logic independently of HTTP requests:

- **BCBP Barcode Decoder**: Test valid strings, invalid lengths, malformed structures, and non-ASCII inputs.
- **Pathfinding**: Test correct edge traversal, elevator-only modes (assert stairs are skipped), and unreachable/disconnected node scenarios.
- **AI Intent Classification**: Mock external Groq LLM responses to avoid hitting real APIs during tests.

### Pathfinding Unit Test Example
```python
def test_pathfinding_elevator_only(test_db):
    # Setup test graph in test_db
    path = wayfinding_service.calculate_route(
        db=test_db, 
        start_node="Gate A", 
        end_node="Lounge", 
        elevator_only=True
    )
    # Assert path contains elevator nodes, not stairs
    assert "Elevator 1" in path
    assert "Stairs 1" not in path
```

## 5. WebSocket/Socket.IO Test Pattern

Test WebRTC signaling using the asyncio Socket.IO client.

```python
import pytest
import socketio
import asyncio

@pytest.mark.asyncio
async def test_socketio_connection():
    sio = socketio.AsyncClient()
    
    events_received = []
    
    @sio.on("offer")
    async def on_offer(data):
        events_received.append(data)
        
    await sio.connect("http://localhost:8000", socketio_path="/sio")
    await sio.emit("offer", {"sdp": "...", "target": "kiosk_1"})
    
    # Let event loop process
    await asyncio.sleep(0.1)
    
    assert len(events_received) > 0
    await sio.disconnect()
```

## 6. Running Tests

Run the test suite using `pytest` from the project root:

- **Run all tests with short tracebacks**: `pytest tests/ -v --tb=short`
- **Run a specific module**: `pytest tests/ -v -k test_flights`
- **Run only unit tests**: `pytest tests/unit/ -v`

## 7. Testing Checklist

- [ ] `conftest.py` uses in-memory SQLite database (`sqlite:///:memory:`).
- [ ] Test isolation is guaranteed (tables created before and dropped after each test).
- [ ] Database dependency `get_db` is overridden using `fastapi_app.dependency_overrides`.
- [ ] Tests cover both happy paths (200) and negative paths (400, 404, 422).
- [ ] External LLM calls are mocked in unit tests.
- [ ] Pathfinding logic includes edge cases (elevator-only, disconnected graphs).
- [ ] Socket.IO events are tested asynchronously.

## Companion Skills Cross-References

| Skill | Purpose |
|-------|---------|
| `fastapi-architecture` | Understand core app structure and dependency injection for testing. |
| `pydantic-validation` | Ensure tests adequately trigger Pydantic validations (422). |
| `webrtc-signaling` | Understand WebRTC/Socket.IO events required in WebSocket tests. |
