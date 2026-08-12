"""
Spatial Indoor Wayfinding REST Router
Provides endpoints for multi-stop Dijkstra path calculation and POI discovery.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from services.pathfinding import pathfinding_engine

router = APIRouter(prefix="/api/v1/wayfinding", tags=["Indoor Wayfinding"])


class RouteRequestPayload(BaseModel):
    origin_node_id: str = Field("kiosk_t3_l1", description="Origin node or kiosk ID", example="kiosk_t3_l1")
    destination_poi_id: str = Field(..., description="Destination POI ID or name", example="Third Wave Coffee")
    accessibility_mode: str = Field("escalator", description="elevator | escalator", example="escalator")
    multi_stops: Optional[List[str]] = Field(default=None, description="Optional intermediate POIs or stops", example=["Medical Centre"])


@router.post("/route")
async def calculate_route(payload: RouteRequestPayload):
    """
    Calculates spatial indoor navigation route using NetworkX Dijkstra algorithm.
    Supports elevator vs escalator accessibility constraints and multi-stop waypoints.
    """
    try:
        route_result = pathfinding_engine.calculate_route(
            origin_node_id=payload.origin_node_id,
            destination_poi_id=payload.destination_poi_id,
            accessibility_mode=payload.accessibility_mode,
            multi_stops=payload.multi_stops
        )
        return {
            "success": True,
            "data": route_result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail={"error": "PATHFINDING_INVALID_REQUEST", "message": str(ve)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "PATHFINDING_SERVER_ERROR", "message": str(e)})


@router.get("/pois")
async def get_airport_pois(
    category: Optional[str] = Query(None, description="Filter by category: dining, shopping, lounges, services, amenities, gates"),
    floor: Optional[str] = Query(None, description="Filter by floor level: L1, L2, Ground")
):
    """
    Retrieves list of airport Points of Interest (POIs) with map coordinates, floor, and metadata.
    """
    try:
        pois = pathfinding_engine.get_pois(category=category, floor=floor)
        return {
            "success": True,
            "count": len(pois),
            "data": pois
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "POI_FETCH_ERROR", "message": str(e)})
