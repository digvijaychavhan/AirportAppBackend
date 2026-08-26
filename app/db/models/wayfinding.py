"""
Spatial Wayfinding, Map & POI Directory ORM Models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.db.base import generate_uuid

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
    sub_category = Column(String, nullable=True)  # cafe, fastfood, electronics, etc.
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
    x_coord = Column(Float, nullable=True)
    y_coord = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    node = relationship("MapNode", back_populates="pois")
    floor = relationship("MapFloor", back_populates="pois")


class WayfindingCategory(Base):
    __tablename__ = "wayfinding_categories"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    icon = Column(String, nullable=False, default="place")
    icon_color = Column(String, nullable=False, default="#2563EB")
    icon_bg = Column(String, nullable=False, default="#DBEAFE")
    route = Column(String, nullable=False)
    subcategories_json = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
