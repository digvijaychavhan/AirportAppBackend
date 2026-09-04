---
name: Backend Async & Performance Optimization
description: Guidelines for managing async/await patterns, preventing event loop blocking, and optimizing performance in the FastAPI backend.
metadata:
  domain: backend
  tags: [async, performance, socketio, database, fastapi]
---

# Backend Async & Performance Optimization

This skill provides guidelines for managing async patterns, protecting the event loop, and optimizing system performance in the Airport Digital Helpdesk FastAPI backend.

## 1. Sync vs Async Decision Tree

The backend currently uses `async def` for endpoint handlers but utilizes a sync SQLAlchemy engine (`create_engine`) and SQLite. 

- **Acceptable (Current State)**: SQLite queries are generally extremely fast (<10ms). The overhead of thread pooling for sync database calls is manageable in single-worker setups for dev/low-traffic environments. Maintain the sync engine for now, but be aware of the architectural tradeoff.
- **When to Migrate**: If migrating to PostgreSQL or anticipating heavy concurrent load, you must switch to `create_async_engine` + `AsyncSession` to prevent database calls from blocking the event loop.

## 2. Blocking I/O Detection & Fixes

Blocking the event loop in `async def` endpoints will stall all concurrent requests. **Never perform synchronous network calls or heavy file I/O directly inside `async def`.**

### Anti-Pattern: Sync HTTP / LLM Clients
Using the synchronous Groq client inside an async endpoint blocks the event loop while waiting for the LLM response.

```python
# ANTI-PATTERN: Blocks the event loop!
from groq import Groq
import requests

@router.post("/chat")
async def chat(request: Request):
    client = Groq(api_key="key")
    response = client.chat.completions.create(...) # BLOCKING
    
    res = requests.get("https://api.example.com") # BLOCKING
```

### Correct Pattern: Async Clients
Always use `AsyncGroq` and `httpx.AsyncClient`.

```python
# CORRECT
from groq import AsyncGroq
import httpx

@router.post("/chat")
async def chat(request: Request):
    client = AsyncGroq(api_key="key")
    response = await client.chat.completions.create(...) # NON-BLOCKING
    
    async with httpx.AsyncClient() as client:
        res = await client.get("https://api.example.com") # NON-BLOCKING
```

### Anti-Pattern: Sync File I/O
```python
# ANTI-PATTERN: Blocks the event loop on slow disks!
@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    data = await file.read()
    with open(f"uploads/{file.filename}", 'wb') as f:
        f.write(data) # BLOCKING
```

### Correct Pattern: Thread Pools or aiofiles
Delegate file writes to a separate thread pool.

```python
# CORRECT
import asyncio

def write_file_sync(path: str, data: bytes):
    with open(path, 'wb') as f:
        f.write(data)

@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    data = await file.read()
    await asyncio.to_thread(write_file_sync, f"uploads/{file.filename}", data)
```

## 3. Graph Singleton Pattern (NetworkX)

The wayfinding module uses NetworkX for pathfinding. Recreating the graph on every request is very inefficient.

### Pattern: Boot-time Singleton
Build the graph once during application startup (Lifespan event) and store it in the app state.

```python
# app/main.py
from fastapi import FastAPI
import networkx as nx
from contextlib import asynccontextmanager

def build_airport_graph() -> nx.Graph:
    G = nx.Graph()
    # Build nodes and edges...
    return G

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.airport_graph = build_airport_graph()
    yield
    # Shutdown
    app.state.airport_graph.clear()

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    # ...
```

**Thread Safety**: NetworkX graphs are safe for concurrent read operations (e.g., shortest path calculations). Rebuild the entire graph and replace `app.state.airport_graph` atomically if map data changes (e.g., via map editor save).

## 4. Socket.IO Configuration

Proper configuration prevents frequent disconnects and allows for scaling.

```python
# CORRECT SOCKET.IO CONFIGURATION
import socketio

# Always set ping_timeout and ping_interval
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*', # Permissive for dev
    ping_timeout=10,
    ping_interval=5
)
```

**Multi-Worker Scaling**:
- In-memory dicts for call state (e.g., WebRTC signaling) will **NOT** work if Uvicorn runs with `--workers > 1`.
- If multi-worker is required, Socket.IO must be backed by a Redis message broker (`client_manager=socketio.AsyncRedisManager('redis://...')`), and call state must be moved to Redis or the database. For single-worker dev environments, the current setup is fine.

## 5. Connection Pooling & Database Performance

When using SQLite with a sync engine in production-like settings, configure the engine to enable Write-Ahead Logging (WAL) and set a busy timeout to prevent "database is locked" errors.

```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Example production-ready SQLite config
engine = create_engine(
    "sqlite:///./airport.db",
    connect_args={
        "check_same_thread": False,
        "timeout": 15 # Busy timeout
    }
)

# Enable WAL mode via event listener
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-10000") # 10MB cache
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## 6. Performance Checklist

- [ ] `AsyncGroq` used instead of `Groq` inside `async def`?
- [ ] `httpx.AsyncClient` used instead of `requests` inside `async def`?
- [ ] File I/O wrapped in `asyncio.to_thread` or using `aiofiles`?
- [ ] NetworkX graph instantiated once at startup and stored in `app.state`?
- [ ] Socket.IO configured with `ping_timeout=10` and `ping_interval=5`?
- [ ] SQLite connection configured with WAL mode and appropriate timeout?

## 7. Companion Skills Cross-References

| Skill | Path | Description |
|-------|------|-------------|
| FastAPI Backend Core | `backend-fastapi-core/SKILL.md` | General FastAPI project structure, routing, and DI patterns. |
| Socket.IO WebRTC | `backend-socketio-webrtc/SKILL.md` | WebRTC signaling implementation over Socket.IO. |
| Database & SQLAlchemy | `backend-database/SKILL.md` | Schema definitions and CRUD operations. |
