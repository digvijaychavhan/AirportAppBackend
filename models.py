from datetime import datetime
import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Kiosk(Base):
    __tablename__ = "kiosks"

    id = Column(String, primary_key=True, default=generate_uuid)
    code = Column(String, unique=True, index=True, nullable=False)
    terminal = Column(String, nullable=False)
    floor_id = Column(String, ForeignKey("map_floors.id"), nullable=False)
    current_node_id = Column(String, ForeignKey("map_nodes.id"), nullable=False)
    is_accessible_ada = Column(Boolean, default=True)
    status = Column(String, default="active")
    last_heartbeat_at = Column(DateTime, default=datetime.utcnow)

    floor = relationship("MapFloor", back_populates="kiosks")
    current_node = relationship("MapNode")


class Airline(Base):
    __tablename__ = "airlines"

    code = Column(String, primary_key=True, index=True)  # e.g., "6E", "AI"
    name = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
    flight_type = Column(String, default="domestic")

    flights = relationship("Flight", back_populates="airline")


class Flight(Base):
    __tablename__ = "flights"

    id = Column(String, primary_key=True, default=generate_uuid)
    flight_number = Column(String, index=True, nullable=False)
    airline_code = Column(String, ForeignKey("airlines.code"), nullable=False)
    origin_iata = Column(String, nullable=False, default="DEL")
    destination_iata = Column(String, nullable=False)
    destination_name = Column(String, nullable=False)
    scheduled_departure = Column(DateTime, nullable=False)
    estimated_departure = Column(DateTime, nullable=True)
    terminal = Column(String, nullable=False)
    gate = Column(String, nullable=False)
    checkin_counters = Column(String, nullable=False)
    baggage_belt = Column(String, nullable=False)
    status = Column(String, default="On Time")

    airline = relationship("Airline", back_populates="flights")


class MapFloor(Base):
    __tablename__ = "map_floors"

    id = Column(String, primary_key=True)  # e.g., "floor-l1"
    building = Column(String, nullable=False, default="Main Terminal")
    floor_level = Column(Integer, nullable=False)
    svg_asset_url = Column(String, nullable=False)

    nodes = relationship("MapNode", back_populates="floor", cascade="all, delete-orphan")
    pois = relationship("Poi", back_populates="floor", cascade="all, delete-orphan")
    kiosks = relationship("Kiosk", back_populates="floor")


class MapNode(Base):
    __tablename__ = "map_nodes"

    id = Column(String, primary_key=True)
    floor_id = Column(String, ForeignKey("map_floors.id"), nullable=False)
    x_coord = Column(Float, nullable=False)
    y_coord = Column(Float, nullable=False)
    zone_name = Column(String, nullable=False)
    is_vertical_connector = Column(Boolean, default=False)
    connector_type = Column(String, nullable=True)  # elevator, escalator, stairs

    floor = relationship("MapFloor", back_populates="nodes")
    pois = relationship("Poi", back_populates="node")


class MapEdge(Base):
    __tablename__ = "map_edges"

    id = Column(String, primary_key=True, default=generate_uuid)
    source_node_id = Column(String, ForeignKey("map_nodes.id"), nullable=False)
    target_node_id = Column(String, ForeignKey("map_nodes.id"), nullable=False)
    distance_meters = Column(Float, nullable=False)
    is_accessible_elevator = Column(Boolean, default=True)
    is_escalator = Column(Boolean, default=False)

    source_node = relationship("MapNode", foreign_keys=[source_node_id])
    target_node = relationship("MapNode", foreign_keys=[target_node_id])


class Poi(Base):
    __tablename__ = "pois"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # eat-dine, shopping, lounge, services, amenities, gates
    sub_category = Column(String, nullable=True) # cafe, fastfood, electronics, etc.
    description = Column(String, nullable=True)
    terminal = Column(String, nullable=True, default="Terminal 3")
    floor_name = Column(String, nullable=True, default="Level 1")
    gate = Column(String, nullable=True)
    distance_m = Column(Integer, default=0)
    badge_label = Column(String, nullable=True)
    badge_variant = Column(String, nullable=True)
    
    node_id = Column(String, ForeignKey("map_nodes.id"), nullable=True)
    floor_id = Column(String, ForeignKey("map_floors.id"), nullable=True)
    operating_hours = Column(String, default="24/7")
    dietary_tags = Column(String, nullable=True)
    rating = Column(Float, default=4.5)
    image_url = Column(String, nullable=True)
    x_coord = Column(Float, nullable=True)  # Optional coordinates
    y_coord = Column(Float, nullable=True)  # Optional coordinates
    is_active = Column(Boolean, default=True)

    node = relationship("MapNode", back_populates="pois")
    floor = relationship("MapFloor", back_populates="pois")


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


class FeedbackSubmission(Base):
    __tablename__ = "feedback_submissions"

    id = Column(String, primary_key=True, default=generate_uuid)
    kiosk_id = Column(String, nullable=True)
    flight_number = Column(String, nullable=True)
    pnr = Column(String, nullable=True)
    overall_rating = Column(Integer, nullable=False)
    cleanliness_rating = Column(Integer, nullable=False)
    staff_rating = Column(Integer, nullable=False)
    wayfinding_rating = Column(Integer, nullable=False)
    wifi_rating = Column(Integer, nullable=False)
    food_rating = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    contact_phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WifiSession(Base):
    __tablename__ = "wifi_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    phone_number = Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    voucher_code = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WayfindingCategory(Base):
    __tablename__ = "wayfinding_categories"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    icon = Column(String, nullable=False, default="place")
    icon_color = Column(String, nullable=False, default="#2563EB")  # Default to blue
    icon_bg = Column(String, nullable=False, default="#DBEAFE")     # Default to light blue
    route = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, default=generate_uuid)
    device_id = Column(String, unique=True, index=True, nullable=False)  # e.g. "KIOSK-T3-L1-04"
    name = Column(String, nullable=False)  # "Kiosk T3-L1-K04 Central Concourse"
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
    kiosk_id = Column(String, index=True, nullable=False)  # e.g. "T3-L1-K04"
    passenger_name = Column(String, nullable=True)  # "Luc Desmarais"
    flight_number = Column(String, index=True, nullable=True)  # "6E 203"
    pnr = Column(String, nullable=True)  # "ABC123"
    seat = Column(String, nullable=True)  # "14B"
    barcode_format = Column(String, default="PDF417_BCBP")  # PDF417_BCBP, QR_CODE, AZTEC
    scan_result = Column(String, nullable=False, default="SUCCESS")  # SUCCESS, FAILED
    failure_reason = Column(String, nullable=True)  # "Corrupted barcode", "Flight expired", "Unreadable checksum"
    raw_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserActionLog(Base):
    __tablename__ = "user_action_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    kiosk_id = Column(String, index=True, nullable=False)  # "T3-L1-K04"
    session_id = Column(String, nullable=True)
    action_type = Column(String, index=True, nullable=False)  # WAYFINDING_SEARCH, VIEW_MAP, START_VIDEO_CALL, etc.
    details = Column(String, nullable=True)  # "Navigated to Third Wave Coffee"
    metadata_json = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
