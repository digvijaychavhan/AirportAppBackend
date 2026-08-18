"""
Legacy Re-Export Wrapper for Database Models
"""

from app.db.models import (
    Kiosk,
    Airline,
    Flight,
    MapFloor,
    MapNode,
    MapEdge,
    Poi,
    WayfindingCategory,
    Operator,
    SupportCall,
    ScreenAnnotation,
    Device,
    ScanLog,
    UserActionLog,
    FeedbackSubmission,
    WifiSession
)
from app.db.base import generate_uuid

__all__ = [
    "Kiosk",
    "Airline",
    "Flight",
    "MapFloor",
    "MapNode",
    "MapEdge",
    "Poi",
    "WayfindingCategory",
    "Operator",
    "SupportCall",
    "ScreenAnnotation",
    "Device",
    "ScanLog",
    "UserActionLog",
    "FeedbackSubmission",
    "WifiSession",
    "generate_uuid"
]
