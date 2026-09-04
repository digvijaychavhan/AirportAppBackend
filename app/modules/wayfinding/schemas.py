"""
Wayfinding Domain Pydantic V2 Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class BaseWayfindingSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class RouteRequestPayload(BaseWayfindingSchema):
    origin_node_id: Optional[str] = Field("node_kiosk_t3_l1_04", alias="originNodeId", description="Origin node ID", json_schema_extra={"example": "node_kiosk_t3_l1_04"})
    destination_poi_id: str = Field(..., alias="destinationPoiId", description="Destination POI or Node ID", json_schema_extra={"example": "poi_gate_b12"})
    accessibility_mode: Optional[str] = Field("elevator", alias="accessibilityMode", description="elevator | escalator", json_schema_extra={"example": "elevator"})
    multi_stops: Optional[List[str]] = Field(default=None, alias="multiStops", description="Optional intermediate stops")


class POISchema(BaseWayfindingSchema):
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


class MapNodeUpdateItem(BaseWayfindingSchema):
    id: str
    x: float
    y: float


class MapNodeUpdatePayload(BaseWayfindingSchema):
    nodes: List[MapNodeUpdateItem]
