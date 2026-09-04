---
name: python-fastapi-backend
description: >-
  Best practices, architecture standards, async performance guidelines, and WebRTC
  signaling patterns for the Python FastAPI backend. Reference this skill when writing,
  reviewing, or refactoring backend code to ensure adherence to the project's modular
  domain-driven architecture.
metadata:
  author: airport-digital-services
  version: "2.0.0"
---

# Python FastAPI Backend — Architecture & Best Practices

This skill outlines the architectural standards, modular code structure, real-time WebRTC signaling conventions, and performance guidelines for the **Airport Digital Helpdesk Backend** (FastAPI, SQLAlchemy, Socket.IO, NetworkX).

---

## 1. Active Project Architecture (Domain-Driven Modules)

The backend uses a **modular domain-driven layout** under `Backend/app/`. The root-level `routes/` directory is legacy dead code and must **never** be used for new work.

```
Backend/
├── main.py                        # ASGI root entrypoint (re-exports app.main)
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app factory, CORS, lifespan, Socket.IO ASGI wrap
│   ├── core/
│   │   ├── config.py              # Pydantic BaseSettings (env vars, secrets)
│   │   ├── database.py            # SQLAlchemy engine, SessionLocal, get_db dependency
│   │   └── logging.py             # Structured logging setup
│   ├── db/
│   │   ├── base.py                # Base, TimestampMixin
│   │   ├── models/                # SQLAlchemy ORM models grouped by domain
│   │   │   ├── __init__.py        # Aggregate model exports
│   │   │   ├── airport.py         # Flight, Airline, Airport, ScanLog
│   │   │   ├── wayfinding.py      # MapNode, MapEdge, Poi, WayfindingCategory
│   │   │   ├── support.py         # SupportCall, Operator, ScreenAnnotation
│   │   │   ├── admin.py           # Kiosk, Device, UserActionLog, QueryTagCategory
│   │   │   ├── feedback.py        # FeedbackSubmission
│   │   │   └── wifi.py            # WifiSession
│   │   ├── migrations.py          # Startup schema migration (column additions)
│   │   └── seed/
│   │       ├── seeder.py          # Idempotent database population engine
│   │       └── data/              # Seed fixture JSON/dictionaries
│   └── modules/                   # ⭐ ACTIVE DOMAIN MODULES
│       ├── __init__.py            # all_routers aggregate list
│       ├── flights/
│       │   ├── __init__.py
│       │   ├── router.py          # Flight search, BCBP decode, gates, baggage
│       │   ├── schemas.py         # Pydantic request/response models
│       │   └── service.py         # IATA BCBP parser, airline/airport lookups
│       ├── wayfinding/
│       │   ├── __init__.py
│       │   ├── router.py          # Indoor routing, POI search, map editor
│       │   ├── schemas.py
│       │   └── service.py         # NetworkX Dijkstra pathfinder engine
│       ├── support/
│       │   ├── __init__.py
│       │   ├── router.py          # Call queue, recordings, operator management
│       │   ├── schemas.py
│       │   └── service.py         # Socket.IO WebRTC signaling state manager
│       ├── admin/
│       │   ├── __init__.py
│       │   ├── router.py          # Kiosk/device management, telemetry, analytics
│       │   └── schemas.py
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── router.py          # Groq LLM intent proxy
│       │   ├── schemas.py
│       │   └── service.py         # AI orchestrator (intent classification, POI context)
│       ├── feedback/
│       │   ├── __init__.py
│       │   ├── router.py          # Passenger survey submission & categories
│       │   └── schemas.py
│       ├── kiosk/
│       │   ├── __init__.py
│       │   ├── router.py          # Telemetry heartbeat endpoint
│       │   └── schemas.py
│       └── wifi/
│           ├── __init__.py
│           ├── router.py          # Wi-Fi OTP generation, passport scanning
│           ├── schemas.py
│           └── service.py         # MRZ passport verification, Groq Vision AI
├── config.py                      # Legacy re-export → app.core.config
├── database.py                    # Legacy re-export → app.core.database
├── models.py                      # Legacy re-export → app.db.models
├── schemas.py                     # Legacy root schemas (⚠️ has import bug)
├── services/                      # Legacy re-export facades → app.modules.*.service
├── routes/                        # ⚠️ DEAD CODE — never imported, never mounted
├── seed.py                        # Root seeder entrypoint
├── requirements.txt
└── Dockerfile
```

> **Rule**: All new code goes into `app/modules/<domain>/`. Never create files in root `routes/` or `services/`.

---

## 2. Module Registration & Router Mounting

New domain routers are registered in two places:

1. **Module `__init__.py`** — Export the router:
   ```python
   # app/modules/<domain>/__init__.py
   from app.modules.<domain>.router import router as <domain>_router
   __all__ = ["<domain>_router"]
   ```

2. **Modules aggregate** — Add to `all_routers` in `app/modules/__init__.py`:
   ```python
   from app.modules.<domain> import <domain>_router
   all_routers = [..., <domain>_router]
   ```

The `app/main.py` factory auto-mounts all routers from `all_routers`:
```python
for router in all_routers:
    app.include_router(router)
```

---

## 3. FastAPI & Async Performance Standards

1. **Native Async Handlers**: Use `async def` for I/O-bound endpoints (database, LLM proxy, WebSockets). However, note that synchronous SQLAlchemy ORM calls inside `async def` block the event loop — use `Depends(get_db)` and keep queries fast, or migrate to async engine for heavy workloads.
2. **Third-Party Async Clients**: Use `AsyncGroq` (not `Groq`) and `httpx.AsyncClient` (not `requests`) inside async handlers to avoid blocking.
3. **Strict Pydantic V2 Models**: Define explicit `response_model` for REST endpoints to prevent accidental data leaks and enable fast JSON serialization.
4. **Dependency Injection**: Always use `Depends(get_db)` for database session lifecycles — never call `SessionLocal()` directly in service functions.
5. **Standardized Error Handling**: Use `HTTPException` with structured JSON payloads and correct HTTP status codes:
   ```python
   raise HTTPException(
       status_code=404,
       detail={"error": "FLIGHT_NOT_FOUND", "message": "Flight 6E 203 not found"}
   )
   ```
   Never return HTTP 200 with `{"success": False}` for error conditions.

---

## 4. WebSockets & WebRTC Signaling Standards

1. **Room Isolation**: Store peer connections in Socket.IO rooms named `call_{call_id}` to prevent signal leakage across parallel calls.
2. **Sub-200ms Signaling Latency**: Handle WebRTC SDP Offer, Answer, and ICE candidate relay events in asynchronous non-blocking memory buffers.
3. **DataChannel Stroke Streaming**: Broadcast screen annotation strokes (`SCREEN_ANNOTATION_STROKE`) immediately to all clients in the call room.
4. **Automatic Reconnection**: Configure `ping_timeout=10, ping_interval=5` on the Socket.IO `AsyncServer` for heartbeat-based disconnect detection.
5. **Multi-Worker Awareness**: In-memory Python dicts for call state are **per-process**. When running with `--workers > 1`, a Redis message broker (`socketio.AsyncRedisManager`) is required for cross-worker signaling.

---

## 5. Indoor Spatial Graph & Pathfinding (`NetworkX`)

1. **Thread-Safe Graph Instance**: Build the multi-floor spatial graph in memory at server boot — do not reconstruct `nx.Graph()` on every request.
2. **Edge Weighting & Constraints**:
   - Distance in meters = edge weight.
   - For `accessibilityMode == 'elevator'`, dynamically filter out stair and escalator edges before running `nx.dijkstra_path()`.
3. **Database Integration**: Route computation must use `MapNode` and `MapEdge` records from the database, not hardcoded fallback nodes.
4. **Structured Response**: Return both raw coordinates for SVG rendering and human-readable step-by-step turn instructions.

---

## 6. CORS & Security

1. **CORS Configuration**: Currently using permissive `allow_origins=["*"]` for development speed. For production, explicitly whitelist trusted origins (`https://airport-app-mocha.vercel.app`, `http://localhost:3000`, Electron app origins).
2. **Environment Isolation**: Load secrets (`GROQ_API_KEY`, `DATABASE_URL`) via Pydantic `BaseSettings` reading from `.env`. Use `SecretStr` for API keys to prevent accidental logging.
3. **Password Storage**: Never store plaintext passwords. Use `passlib[bcrypt]` or `argon2-cffi` for hashing.
4. **Input Sanitization**: Validate path parameters with regex constraints to prevent directory traversal in file upload/download endpoints.

---

## 7. Companion Skills & Cross-References

| Stage | Companion Skill | What to check |
| :--- | :--- | :--- |
| **Adding a New Module** | `backend-feature-development` | Step-by-step scaffolding, templates, registration, quality checklist |
| **Security & Auth** | `backend-security-hardening` | Password hashing, auth dependencies, input validation, secrets |
| **Testing** | `backend-testing-standards` | Fixtures, negative tests, WebSocket tests, coverage targets |
| **Async & Performance** | `backend-async-performance` | Blocking I/O detection, async clients, graph singletons, pooling |
| **Database & Migrations** | `backend-database-patterns` | Session lifecycle, Alembic, column types, seed safety |
| **API Response Design** | `backend-api-design-contracts` | Response envelope, HTTP status codes, error payloads, pagination |
