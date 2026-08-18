"""
Wayfinding Domain Pydantic V2 Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class RouteRequestPayload(BaseModel):
    origin_node_id: Optional[str] = Field("node_kiosk_t3_l1_04", alias="originNodeId", description="Origin node ID", example="node_kiosk_t3_l1_04")
    destination_poi_id: str = Field(..., alias="destinationPoiId", description="Destination POI or Node ID", example="poi_gate_b12")
    accessibility_mode: Optional[str] = Field("elevator", alias="accessibilityMode", description="elevator | escalator", example="elevator")
    multi_stops: Optional[List[str]] = Field(default=None, alias="multiStops", description="Optional intermediate stops")

    class Config:
        populate_by_name = True

class POISchema(BaseModel):
    id: str
    name: str
    category: str
    category_label: Optional[str] = Field(None, alias="categoryLabel")
    sub_category: Optional[str] = Field(None, alias="subCategory")
    description: Optional[str] = None
    is_open: bool = Field(True, alias="isOpen")
    hours: Optional[str] = "24 Hours"
    terminal: Optional[str] = ""
    floor: Optional[str] = ""
    gate: Optional[str] = ""
    distance_m: Optional[int] = Field(100, alias="distanceM")
    image: Optional[str] = ""
    badge: Optional[str] = ""
    badge_variant: Optional[str] = Field("purple", alias="badgeVariant")
    filter: Optional[List[str]] = []

    class Config:
        populate_by_name = True

class MapNodeUpdateItem(BaseModel):
    id: str
    x: float
    y: float

class MapNodeUpdatePayload(BaseModel):
    nodes: List[MapNodeUpdateItem]
