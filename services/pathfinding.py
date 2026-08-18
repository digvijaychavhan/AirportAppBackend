"""
Legacy Re-Export Wrapper for Pathfinding Engine
"""

from app.modules.wayfinding.service import (
    AIRPORT_POIS,
    compute_indoor_route,
    pathfinding_engine,
    PathfindingEngine
)

__all__ = [
    "AIRPORT_POIS",
    "compute_indoor_route",
    "pathfinding_engine",
    "PathfindingEngine"
]
