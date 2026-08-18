"""
Customer Support, Operator Workforce & WebRTC Annotation ORM Models
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.db.base import generate_uuid

class Operator(Base):
    __tablename__ = "operators"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True, nullable=True)
    employee_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, default="operator123")
    role = Column(String, default="Assistant")
    status = Column(String, default="available")  # available, busy, offline
    supported_languages = Column(String, default="English, Hindi")
    calls_handled = Column(Integer, default=0)
    avg_handle_time = Column(String, default="2m 30s")
    resolution_rate = Column(String, default="98%")
    shift = Column(String, default="Morning (06:00 - 14:00)")
    created_at = Column(DateTime, default=datetime.utcnow)

    calls = relationship("SupportCall", back_populates="operator")


class SupportCall(Base):
    __tablename__ = "support_calls"

    id = Column(String, primary_key=True, default=generate_uuid)
    kiosk_id = Column(String, ForeignKey("kiosks.id"), nullable=False)
    operator_id = Column(String, ForeignKey("operators.id"), nullable=True)
    status = Column(String, default="queued")  # queued, active, ended, missed
    ada_priority = Column(Boolean, default=False)
    requested_language = Column(String, default="English")
    wait_duration_seconds = Column(Integer, default=0)
    call_duration_seconds = Column(Integer, default=0)
    issue_category = Column(String, nullable=True)
    operator_notes = Column(Text, nullable=True)
    passenger_name = Column(String, nullable=True)
    flight_number = Column(String, nullable=True)
    pnr = Column(String, nullable=True)
    recording_url = Column(String, nullable=True)
    recording_duration_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    kiosk = relationship("Kiosk")
    operator = relationship("Operator", back_populates="calls")
    annotations = relationship("ScreenAnnotation", back_populates="call", cascade="all, delete-orphan")


class ScreenAnnotation(Base):
    __tablename__ = "screen_annotations"

    id = Column(String, primary_key=True, default=generate_uuid)
    call_id = Column(String, ForeignKey("support_calls.id"), nullable=False)
    stroke_data = Column(Text, nullable=False)  # JSON string of canvas strokes
    created_at = Column(DateTime, default=datetime.utcnow)

    call = relationship("SupportCall", back_populates="annotations")
