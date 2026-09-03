---
name: python-fastapi-backend
description: Best practices, architecture standards, async performance guidelines, and WebRTC signaling patterns for Python FastAPI backends.
---

# Python FastAPI Backend Guidelines & Best Practices

This skill outlines the architectural standards, code structure, real-time WebRTC signaling conventions, and performance guidelines for building high-speed, enterprise-grade Python FastAPI backends.

---

## 1. Project Directory Architecture

Keep the project modular and domain-driven:

```
Backend/
├── main.py                # ASGI application bootstrap & CORS setup
├── config.py              # Environment variables & Pydantic BaseSettings
├── database.py            # SQLAlchemy database engine & session sessionmaker
├── models.py              # SQLAlchemy ORM database models
├── schemas.py             # Pydantic v2 validation & response schemas
├── routes/                # REST API endpoints grouped by domain
│   ├── flights.py         # Flight search & BCBP barcode decoding
│   ├── wayfinding.py      # Spatial Dijkstra pathfinding API
│   ├── support.py         # Support call queue management APIs
│   ├── ai.py              # Groq AI intent proxy
│   ├── feedback.py       # Passenger survey API
│   └── wifi.py            # Wi-Fi guest portal OTP endpoints
├── services/              # Pure business logic & service engines
│   ├── webrtc_signaling.py# Socket.IO & WebRTC room/SDP state manager
│   ├── pathfinding.py     # NetworkX spatial graph pathfinder engine
│   ├── bcbp_decoder.py    # IATA 2D barcode PDF417 parser
│   └── ai_orchestrator.py # Groq LLM API proxy
├── seed.py                # Database population script
├── requirements.txt       # Python dependencies
└── Dockerfile             # Docker container definition for Cloud deployment
```

---

## 2. FastAPI & Async Performance Standards

1. **Native Async Handlers**: Use `async def` for I/O bound endpoints (database calls, LLM proxy, WebSockets) to prevent blocking Uvicorn's event loop.
2. **Strict Pydantic V2 Models**: Always define explicit `response_model` for REST endpoints to prevent accidental data leaks and maintain high-speed JSON serialization.
3. **Dependency Injection**: Use `Depends(get_db)` for database session lifecycles to ensure proper connection cleanup.
4. **Standardized Error Handling**: Use `HTTPException` with structured JSON payloads:
   ```python
   raise HTTPException(status_code=404, detail={"error": "FLIGHT_NOT_FOUND", "message": "Flight 6E 203 not found"})
   ```

---

## 3. WebSockets & WebRTC Signaling Standards

1. **Room Isolation**: Store peer connections in Socket.IO rooms named `call_{call_id}` to prevent signal leakage across parallel calls.
2. **Sub-200ms Signaling Latency**: Handle WebRTC SDP Offer, Answer, and ICE candidate relay events in asynchronous non-blocking memory buffers.
3. **DataChannel Stroke Streaming**: Broadcast screen annotation strokes (`SCREEN_ANNOTATION_STROKE`) immediately to all clients in the call room.
4. **Automatic Reconnection**: Gracefully handle disconnected sockets with client ping/pong heartbeats (`ping_timeout=10`, `ping_interval=5`).

---

## 4. Indoor Spatial Graph & Pathfinding (`NetworkX`)

1. **Thread-Safe Graph Instance**: Build the multi-floor spatial graph in memory at server boot.
2. **Edge Weighting & Constraints**:
   - Distance in meters = edge weight.
   - For `accessibilityMode == 'elevator'`, dynamically filter out stair and escalator edges before running `nx.dijkstra_path()`.
3. **Structured Response**: Return both raw coordinates for SVG rendering and human-readable step-by-step turn instructions.

---

## 5. Security & Deployment

1. **CORS Hardening**: Explicitly whitelist trusted origins (`http://localhost:3000`, mobile app domains).
2. **Environment Isolation**: Load secrets (`GROQ_API_KEY`, `DATABASE_URL`) via Pydantic `BaseSettings` reading from `.env`.
3. **Production Containerization**: Use `uvicorn main:app --host 0.0.0.0 --port 5000 --workers 4` for multi-worker container deployments on Oracle Cloud Infrastructure (OCI).
