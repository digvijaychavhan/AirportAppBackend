"""
Declarative Base & Model Helper Utilities
"""

import uuid
from sqlalchemy import Column, DateTime, String
from app.core.database import Base
from app.core.timezone import get_current_time

def generate_uuid() -> str:
    return str(uuid.uuid4())

class TimestampMixin:
    """Mixin that adds created_at timestamp in IST to ORM models."""
    created_at = Column(DateTime, default=get_current_time, nullable=False)
