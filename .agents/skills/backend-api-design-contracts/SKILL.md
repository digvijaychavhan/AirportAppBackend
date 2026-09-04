---
name: backend-api-design-contracts
description: API response contracts, HTTP status code usage, error handling patterns, and endpoint design standards.
---

# API Design Contracts & Standards

This document defines the API response contracts, HTTP status code taxonomy, error handling, and endpoint design standards for the Airport Digital Helpdesk FastAPI backend.

## 1. Universal Response Envelope

All successful API endpoints must return a consistent envelope containing `success` and `data`. Never return HTTP 200 with `{"success": false}` for errors; use `HTTPException` instead.

### Pattern: Generic API Response
Use a generic Pydantic model for standard responses:

```python
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
```

### Usage in Routes
```python
from fastapi import APIRouter
from app.modules.flights.schemas import FlightData
from app.core.schemas import ApiResponse # Assuming generic response is located here

router = APIRouter(prefix="/flights", tags=["Flights"])

@router.get("/{flight_id}", response_model=ApiResponse[FlightData])
def get_flight(flight_id: str):
    # logic
    flight = get_flight_from_db(flight_id)
    return ApiResponse(success=True, data=flight)
```

## 2. HTTP Status Code Taxonomy

Use the correct HTTP status codes to reflect the outcome of the request.

- **200 OK**: Successful `GET`, `PUT`, or `PATCH`.
- **201 Created**: Successful `POST` where a resource is created.
- **204 No Content**: Successful `DELETE` (no response body).
- **400 Bad Request**: Client error (malformed request, invalid business logic state).
- **404 Not Found**: The requested resource does not exist.
- **422 Unprocessable Entity**: Pydantic validation failure (handled automatically by FastAPI).
- **500 Internal Server Error**: Unhandled server error.

> [!WARNING]
> **Anti-Pattern**: Returning `HTTP 200` with `{"success": false, "error": "Something went wrong"}`. Always raise an HTTP error code when the action fails.

## 3. Structured Error Payloads

When throwing errors, use FastAPI's `HTTPException` and include a structured `detail` dictionary with an error code and message.

### Error Code Convention
Error codes should use `SCREAMING_SNAKE_CASE`. Common codes include: `NOT_FOUND`, `VALIDATION_ERROR`, `UNAUTHORIZED`, `FORBIDDEN`, `INTERNAL_ERROR`.

### Pattern: HTTPException
```python
from fastapi import HTTPException, status

@router.get("/{flight_id}")
def get_flight(flight_id: str):
    flight = get_flight_from_db(flight_id)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Flight {flight_id} not found"}
        )
    return ApiResponse(success=True, data=flight)
```

## 4. Endpoint Design Standards

Follow RESTful conventions for route definitions.

- **Resource Naming**: Use plural nouns (e.g., `/api/v1/flights`, `/api/v1/users`).
- **Versioned Prefix**: Every module router should be mounted under `/api/v1/`.
- **Consistent Route Patterns**:
  - `GET /resource` (List)
  - `GET /resource/{id}` (Retrieve)
  - `POST /resource` (Create)
  - `PUT /resource/{id}` (Update)
  - `DELETE /resource/{id}` (Destroy)
- **Swagger Grouping**: Use `tags` in `APIRouter` to organize the Swagger UI.
- **Creation Endpoints**: Explicitly define `status_code=201` for POST creation endpoints.

### Pattern: Standard Router
```python
from fastapi import APIRouter, status

router = APIRouter(prefix="/waypoints", tags=["Wayfinding"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[WaypointData])
def create_waypoint(data: WaypointCreate):
    # logic
    pass
```

## 5. Pagination Pattern

Never return an unbounded list of database records. Use standard query parameters for pagination.

- **limit**: Number of records to return (default 50, max 200).
- **offset**: Number of records to skip (default 0).

### Pattern: Paginated Response
```python
from pydantic import BaseModel
from typing import TypeVar, Generic, List

T = TypeVar('T')

class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    pagination: PaginationMeta

@router.get("/", response_model=PaginatedResponse[FlightData])
def list_flights(limit: int = 50, offset: int = 0):
    limit = min(limit, 200) # enforce maximum
    flights, total = db_list_flights(limit, offset)
    return PaginatedResponse(
        success=True,
        data=flights,
        pagination=PaginationMeta(total=total, limit=limit, offset=offset)
    )
```

## 6. `response_model` Enforcement

Every route MUST declare a `response_model` or have a strictly typed return annotation. This prevents accidental data leaks (e.g., exposing password hashes from a database model) and generates accurate OpenAPI schemas.

> [!TIP]
> Use `response_model_exclude_none=True` in route decorators to omit `null` fields from the response, saving bandwidth and simplifying client parsing.

### Pattern: Strict Response Models
```python
@router.get("/{user_id}", response_model=ApiResponse[UserProfile], response_model_exclude_none=True)
def get_user_profile(user_id: str):
    # Only fields defined in UserProfile will be returned, preventing leakage
    # of sensitive fields present in the raw database model.
    user = get_user(user_id)
    return ApiResponse(success=True, data=user)
```

## 7. API Design Checklist

Before submitting PRs or finalizing API endpoints, verify:
- [ ] Envelope `{"success": true, "data": ...}` is used for success responses.
- [ ] Correct HTTP status codes are used (201 for POST, etc.).
- [ ] No `HTTP 200` responses with `success: false`.
- [ ] `HTTPException` is raised for errors with `detail` containing `error` and `message`.
- [ ] Plural nouns are used for resource paths.
- [ ] `response_model` is explicitly declared on all route decorators.
- [ ] Pagination (`limit`/`offset`) is implemented on endpoints returning lists.
- [ ] Pydantic V2 `model_config` is used instead of V1 `class Config`.

## 8. Companion Skills Cross-References

| Skill | Description |
|-------|-------------|
| `backend-pydantic-v2-migration` | Pydantic V2 model creation and configuration patterns |
| `backend-database-sqlalchemy` | SQLAlchemy querying and pagination logic |
| `backend-fastapi-routers` | Router registration and modular app structure |
