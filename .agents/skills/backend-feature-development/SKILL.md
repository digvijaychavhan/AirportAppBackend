---
name: Backend Feature Development
description: Complete step-by-step workflow for adding a new API domain module to the backend using the module slice architecture.
metadata:
  target_audience: AI Agents
  version: "1.0"
---

# Backend Feature Development

This skill defines the canonical workflow for adding new features or API domains to the Airport Digital Helpdesk FastAPI backend. We use a **domain-driven module slice architecture** where all code related to a specific domain lives together.

## 1. Module Slice Directory Layout

Every domain must be fully encapsulated in its own directory under `app/modules/`.

```
app/modules/<domain>/
├── __init__.py        # Exports the router
├── router.py          # FastAPI APIRouter, dependencies, route definitions
├── schemas.py         # Pydantic V2 models for requests/responses
├── service.py         # Pure business logic and DB operations
└── models.py          # SQLAlchemy ORM models (only if new tables needed)
```

## 2. Step-by-Step Workflow

When building a new domain, follow this exact sequence:

```mermaid
flowchart TD
    A[1. Define Schemas (schemas.py)] --> B[2. Define Models (models.py)]
    B --> C[3. Implement Service (service.py)]
    C --> D[4. Create Router (router.py)]
    D --> E[5. Export Router (__init__.py)]
    E --> F[6. Register Router (app/modules/__init__.py)]
    F --> G[7. DB Migrations & Seeding]
    G --> H[8. Write Tests]
```

1. **Define Pydantic schemas**: Create request/response models using Pydantic V2.
2. **Create SQLAlchemy models**: If the feature requires new database tables.
3. **Implement service layer**: Pure business logic that takes `db: Session` as a parameter.
4. **Create router**: Define endpoints with `APIRouter(tags=["Domain"])`, proper `response_model`, and `Depends(get_db)`.
5. **Export in module**: Make the router accessible in `__init__.py`.
6. **Register router**: Add to the `all_routers` list in `app/modules/__init__.py`.
7. **Database updates**: Add migration columns in `app/db/migrations.py` and seed data in `app/db/seed/` if needed.
8. **Write tests**: Implement unit/integration tests for the new module.

## 3. Code Templates

### `schemas.py` (Pydantic V2)
```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class FeatureBase(BaseModel):
    name: str = Field(..., description="Name of the feature")
    is_active: bool = True

class FeatureCreate(FeatureBase):
    pass

class FeatureResponse(FeatureBase):
    id: int
    
    # Pydantic V2 syntax for ORM mode
    model_config = ConfigDict(from_attributes=True)
```

### `service.py` (Pure Business Logic)
```python
from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

# Takes `db: Session` as a parameter, NEVER calls SessionLocal()
def get_features(db: Session) -> List[models.Feature]:
    return db.query(models.Feature).all()

def create_feature(db: Session, feature: schemas.FeatureCreate) -> models.Feature:
    db_feature = models.Feature(**feature.model_dump())
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature
```

### `router.py` (FastAPI Endpoints)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from . import schemas, service

router = APIRouter(prefix="/api/features", tags=["Features"])

@router.get("/", response_model=List[schemas.FeatureResponse])
def read_features(db: Session = Depends(get_db)):
    return service.get_features(db)

@router.post("/", response_model=schemas.FeatureResponse, status_code=status.HTTP_201_CREATED)
def create_feature(
    feature: schemas.FeatureCreate,
    db: Session = Depends(get_db)
):
    try:
        return service.create_feature(db, feature)
    except Exception as e:
        # Proper error handling mapping to HTTP status codes
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

### `__init__.py` (Module Export)
```python
from .router import router

__all__ = ["router"]
```

## 4. Universal Response Envelope

While FastAPI handles simple JSON serialization, many client applications expect a universal response envelope. When implementing standard API endpoints that are consumed by the frontend, adhere to this contract:

**Success Response:**
```json
{
  "success": true,
  "data": { "id": 1, "name": "Feature 1" }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Invalid input provided"
}
```

*Note: For standard REST routes, `response_model` handles returning the `data` payload directly. Custom middleware or decorators can be used to wrap responses in this envelope if required globally.*

## 5. Anti-Patterns (What NOT to do)

- ❌ **Legacy Directories:** Never create files in root `routes/` or `services/`. Those are legacy directories. All new code goes into `app/modules/<domain>/`.
- ❌ **Manual DB Sessions:** Never call `SessionLocal()` inside service functions. The `db` session must always be injected from the router via `Depends(get_db)` and passed to the service as an argument.
- ❌ **HTTP 200 Errors:** Never return HTTP 200 with `{"success": False}` for errors. Always raise an `HTTPException` with the correct HTTP status code (e.g., 400, 404, 500).
- ❌ **Legacy Pydantic V1:** Never use `class Config:` in Pydantic models. We use Pydantic V2, so always use `model_config = ConfigDict(...)`.
- ❌ **HTTP Leakage:** The `service.py` file should have zero HTTP imports. Do not import `HTTPException`, `Request`, or anything from `fastapi` in the service layer.

## 6. Quality Checklist

- [ ] Module is completely self-contained in `app/modules/<domain>/`
- [ ] Every route has an explicit `response_model` or typed return
- [ ] Service layer has zero HTTP imports (no `HTTPException`, no `fastapi`)
- [ ] All DB access uses `Depends(get_db)` passed down from router, not `SessionLocal()`
- [ ] Structured `HTTPException` errors are used with correct HTTP status codes
- [ ] Schemas use Pydantic V2 `model_config = ConfigDict(from_attributes=True)` instead of `class Config:`
- [ ] Module router is correctly registered in `app/modules/__init__.py` -> `all_routers` list
- [ ] Tests are written covering both the happy path and error cases

## 7. Companion Skills Cross-References

| Skill | Description |
|-------|-------------|
| `backend-database-management` | Working with SQLAlchemy models, migrations, and seed data |
| `backend-error-handling` | Standardized error formats and HTTP status codes |
| `backend-testing` | Pytest fixtures, DB mocking, and API testing strategies |
