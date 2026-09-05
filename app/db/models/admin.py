"""
Device Fleet, Scan Logs & User Action Audit ORM Models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from app.core.database import Base
from app.db.base import generate_uuid, TimestampMixin
from app.core.timezone import get_current_time

class Device(Base, TimestampMixin):
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
    status = Column(String, default="offline")  # online, warning, offline
    runtime_env = Column(String, default="browser", nullable=True)  # electron, browser
    
    # Hardware Diagnostics
    scanner_connected = Column(Boolean, nullable=True)
    scanner_working = Column(String, nullable=True)  # OK, ERROR, DISCONNECTED, N/A
    scanner_status = Column(String, nullable=True)
    
    camera_connected = Column(Boolean, nullable=True)
    camera_working = Column(String, nullable=True)  # OK, ERROR, DISCONNECTED, N/A
    camera_status = Column(String, nullable=True)
    
    screen_status = Column(String, default="OK")
    
    # System Resources & Network (Real stats from Electron, null in Browser mode)
    cpu_pct = Column(Float, nullable=True)
    ram_used_mb = Column(Float, nullable=True)
    ram_total_mb = Column(Float, nullable=True)
    ram_pct = Column(Float, nullable=True)
    network_bandwidth_mbps = Column(Float, nullable=True)
    ping_ms = Column(Integer, nullable=True, default=None)
    
    last_heartbeat = Column(DateTime, nullable=True, default=None)


class ScanLog(Base, TimestampMixin):
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


class UserActionLog(Base, TimestampMixin):
    __tablename__ = "user_action_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    kiosk_id = Column(String, index=True, nullable=False, default="T3-L1-K04")
    username = Column(String, index=True, nullable=True)  # Passenger name / username if logged in; None for Guest
    session_id = Column(String, nullable=True)
    action_type = Column(String, index=True, nullable=False, default="CLICK")  # CLICK, PAGE_VIEW, SCAN, SEARCH, NAVIGATION
    target_element = Column(String, nullable=True)  # Button label, link, chip name, etc.
    route = Column(String, nullable=True)  # Current route e.g. /eat-dine, /wayfinding/shopping
    details = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)

