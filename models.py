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
    category = Column(String, nullable=False)  # Dining, Retail, Lounge, Restroom, Gate, etc.
    node_id = Column(String, ForeignKey("map_nodes.id"), nullable=False)
    floor_id = Column(String, ForeignKey("map_floors.id"), nullable=False)
    operating_hours = Column(String, default="24/7")
    dietary_tags = Column(String, nullable=True)
    rating = Column(Float, default=4.5)
    image_url = Column(String, nullable=True)

    node = relationship("MapNode", back_populates="pois")
    floor = relationship("MapFloor", back_populates="pois")


class Operator(Base):
    __tablename__ = "operators"

    id = Column(String, primary_key=True, default=generate_uuid)
    employee_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="Assistant")
    status = Column(String, default="available")  # available, busy, offline
    supported_languages = Column(String, default="English, Hindi")

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
