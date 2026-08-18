"""
Device Fleet, Scan Logs & User Action Audit ORM Models
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.core.database import Base
from app.db.base import generate_uuid

class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, default=generate_uuid)
    device_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    device_type = Column(String, default="kiosk")  # kiosk, operator_terminal, scanner, display
    ip_address = Column(String, default="192.168.1.104")
    mac_address = Column(String, default="00:1A:2B:3C:4D:5E")
    terminal = Column(String, default="Terminal 3")
    floor_name = Column(String, default="Level 1")
    location = Column(String, default="Near Gate B12")
    status = Column(String, default="online")  # online, warning, offline
    ping_ms = Column(Integer, default=12)
    cpu_pct = Column(Integer, default=24)
    ram_pct = Column(Integer, default=48)
    screen_status = Column(String, default="OK")
    scanner_status = Column(String, default="OK")
    camera_status = Column(String, default="OK")
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScanLog(Base):
    __tablename__ = "scan_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    kiosk_id = Column(String, index=True, nullable=False)
    passenger_name = Column(String, nullable=True)
    flight_number = Column(String, index=True, nullable=True)
    pnr = Column(String, nullable=True)
    seat = Column(String, nullable=True)
    barcode_format = Column(String, default="PDF417_BCBP")
    scan_result = Column(String, nullable=False, default="SUCCESS")  # SUCCESS, FAILED
    failure_reason = Column(String, nullable=True)
    raw_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserActionLog(Base):
    __tablename__ = "user_action_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    kiosk_id = Column(String, index=True, nullable=False)
    session_id = Column(String, nullable=True)
    action_type = Column(String, index=True, nullable=False)
    details = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
