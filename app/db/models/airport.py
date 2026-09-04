"""
Airport, Flights & Kiosk Domain ORM Models
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.db.base import generate_uuid
from app.core.timezone import get_current_time

class Kiosk(Base):
    __tablename__ = "kiosks"

    id = Column(String, primary_key=True, default=generate_uuid)
    code = Column(String, unique=True, index=True, nullable=False)
    terminal = Column(String, nullable=False)
    floor_id = Column(String, ForeignKey("map_floors.id"), nullable=False)
    current_node_id = Column(String, ForeignKey("map_nodes.id"), nullable=False)
    is_accessible_ada = Column(Boolean, default=True)
    status = Column(String, default="active")
    last_heartbeat_at = Column(DateTime, default=get_current_time)

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


class Airport(Base):
    __tablename__ = "airports"

    iata_code = Column(String, primary_key=True, index=True)  # e.g., "DEL", "BOM", "PNQ"
    city = Column(String, nullable=False)
    name = Column(String, nullable=False)
    country = Column(String, default="India")
    is_active = Column(Boolean, default=True)

