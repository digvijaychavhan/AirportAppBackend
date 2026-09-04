---
name: Backend Database Patterns
description: Guidelines for database session management, model standards, migrations, and safe seed scripts in the FastAPI backend.
metadata:
  domain: database
  framework: SQLAlchemy, SQLite
---

# Backend Database Patterns

This document establishes the patterns for interacting with the database in the FastAPI application. It covers connection management, schema definition, migration strategies, and data seeding to prevent connection leaks, data loss, and deprecated patterns.

## 1. Session Lifecycle — The Golden Rule

**Rule:** NEVER call `SessionLocal()` directly inside service functions or routers. Always inject the session via FastAPI's `Depends(get_db)` and pass it down as a parameter.

Calling `SessionLocal()` without a `try/finally` block to close the session leads to connection leaks, eventually halting the application.

### The Dependency (in `app/core/database.py`)
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### ❌ Anti-pattern: Direct Instantiation (Connection Leak)
```python
# app/modules/flights/service.py
from app.core.database import SessionLocal

def get_flight_status(flight_id: str):
    # BAD: No cleanup, leaks a connection on every call
    db = SessionLocal() 
    return db.query(Flight).filter(Flight.id == flight_id).first()
```

### ✅ Correct Pattern: Dependency Injection
```python
# app/modules/flights/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.flights import service

@router.get("/{flight_id}")
def get_flight(flight_id: str, db: Session = Depends(get_db)):
    return service.get_flight_status(db, flight_id)

# app/modules/flights/service.py
from sqlalchemy.orm import Session

def get_flight_status(db: Session, flight_id: str):
    # GOOD: Session lifecycle is managed by the FastAPI request scope
    return db.query(Flight).filter(Flight.id == flight_id).first()
```

## 2. Model Standards

When creating or updating models in `app/db/models/`, adhere to the following standards:

1. **Use `TimestampMixin`:** Do not manually declare `created_at` or `updated_at`. Inherit from `TimestampMixin` located in `app/db/base.py`.
2. **Modern Datetimes:** Use `datetime.now(timezone.utc)` instead of the deprecated `datetime.utcnow`.
3. **Structured Data:** Use SQLAlchemy's `JSON` type for lists, dictionaries, or structured configuration instead of `String` or `Text`. Reserve `Text` for actual long-form text (e.g., descriptions, feedback bodies).

### ✅ Well-Structured Model Template
```python
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, JSON
from app.db.base import Base, TimestampMixin

class WayfindingPOI(Base, TimestampMixin):
    __tablename__ = "pois"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # GOOD: Using JSON type for structured data, not String/Text
    metadata_config = Column(JSON, default=dict) 
    tags = Column(JSON, default=list)
```

## 3. Migration Strategy

We currently use a custom migration script (`app/db/migrations.py`) that utilizes `sqlite3.PRAGMA table_info()` to handle schema changes. While simple, it requires careful manual management.

*Note: This approach is tightly coupled to SQLite and won't work out-of-the-box if migrating to PostgreSQL.*

### How to Add a Column Safely
When adding a new column to an existing model, you must update `app/db/migrations.py` to ensure the column is added without dropping the table.

```python
# app/db/migrations.py template
import sqlite3

def run_migrations(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check if column exists
    cursor.execute("PRAGMA table_info(pois)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # 2. Add column if it's missing
    if "metadata_config" not in columns:
        print("Migrating: Adding metadata_config to pois")
        cursor.execute("ALTER TABLE pois ADD COLUMN metadata_config JSON DEFAULT '{}'")
        
    conn.commit()
    conn.close()
```

## 4. Seed Script Safety

Seed scripts populate initial data. They must be safe to run against production databases.

**Rule:** NEVER delete the database file (e.g., `os.remove('app.db')`) within a seed script. 

### ✅ Safe, Idempotent Seeding Template
```python
# app/db/seed/seeder.py
from sqlalchemy.orm import Session
from app.db.models.wayfinding import WayfindingPOI

def seed_pois(db: Session, force: bool = False):
    seed_data = [{"id": "gate_a1", "name": "Gate A1"}]
    
    for item in seed_data:
        existing = db.query(WayfindingPOI).filter(WayfindingPOI.id == item["id"]).first()
        
        if existing and not force:
            continue # Safe: Skip if exists
            
        if existing and force:
            existing.name = item["name"] # Safe: Update if forced
        else:
            new_poi = WayfindingPOI(**item)
            db.add(new_poi) # Safe: Insert new
            
    db.commit()
```

## 5. SQLite-Specific Best Practices

Since the application uses SQLite natively, ensure the engine configuration in `app/core/database.py` includes settings to handle concurrency effectively:

```python
from sqlalchemy import create_engine

# SQLite requires specific args for multi-threading and concurrency
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False, # Required for FastAPI multi-threading
        "timeout": 30 # Wait up to 30s for lock instead of raising OperationalError
    }
)

# Enable WAL (Write-Ahead Logging) for better read/write concurrency
from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()
```

*Note on Concurrency: SQLite only allows one writer at a time. Under heavy concurrent write loads, the `timeout` parameter prevents immediate failures, but prolonged locking can still cause bottlenecks.*

## Database Checklist

- [ ] Does the service function accept `db: Session` rather than calling `SessionLocal()`?
- [ ] Is `Depends(get_db)` used in the router endpoint?
- [ ] Does the new model inherit from `TimestampMixin`?
- [ ] Is `JSON` used for structured columns instead of `String`?
- [ ] Are datetime fields using `datetime.now(timezone.utc)`?
- [ ] Are seed scripts idempotent (checking existence before insertion)?
- [ ] Does `app/core/database.py` configure `check_same_thread=False` and `timeout`?

## Companion Skills Cross-References

| Skill | Purpose |
|-------|---------|
| `backend-architecture` | Domain module structure and dependency injection boundaries |
| `api-standards` | How to structure Pydantic schemas and map them to ORM models |
