"""
Declarative Base & Model Helper Utilities
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class TimestampMixin:
    """Mixin that adds created_at timestamp to ORM models."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
