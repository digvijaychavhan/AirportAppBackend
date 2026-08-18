"""
Wayfinding & Indoor Spatial Navigation REST Router
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.logging import logger
import app.db.models as models
from app.modules.wayfinding.schemas import RouteRequestPayload, MapNodeUpdatePayload
from app.modules.wayfinding.service import compute_indoor_route, pathfinding_engine

router = APIRouter(tags=["Indoor Wayfinding"])

@router.post("/api/v1/wayfinding/route")
async def calculate_wayfinding_route(payload: RouteRequestPayload):
    """
    Computes optimal multi-floor indoor walking route using NetworkX Dijkstra algorithm.
    """
    try:
        origin = payload.origin_node_id or "node_kiosk_t3_l1_04"
        dest = payload.destination_poi_id
        mode = payload.accessibility_mode or "elevator"
        result = compute_indoor_route(
            origin_node_id=origin,
            destination_poi_id=dest,
            accessibility_mode=mode,
            multi_stops=payload.multi_stops
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "PATHFINDING_INVALID_REQUEST", "message": str(ve)}
        )
    except Exception as e:
        logger.error(f"Wayfinding calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "PATHFINDING_SERVER_ERROR", "message": str(e)}
        )


@router.get("/api/v1/wayfinding/pois")
async def get_airport_pois(
    category: Optional[str] = Query(None, description="dining, shopping, lounges, services, amenities, gates"),
    floor: Optional[str] = Query(None, description="L1, L2, Ground")
):
    """
    Retrieves POIs with coordinates and metadata.
    """
    pois = pathfinding_engine.get_pois(category=category, floor=floor)
    return {"success": True, "count": len(pois), "data": pois}


@router.get("/api/v1/directory")
async def get_directory_pois(
    category: Optional[str] = Query(None, description="Category filter (e.g. eat-dine, shopping, lounge)"),
    db: Session = Depends(get_db)
):
    """
    Fetches categorized directory points of interest from SQL database.
    """
    try:
        query = db.query(models.Poi)
        if category and category.strip():
            query = query.filter(models.Poi.category.ilike(category.strip()))

        pois = query.all()

        data = [{
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "categoryLabel": p.sub_category or p.category,
            "subCategory": p.sub_category or "",
            "description": p.description or "",
            "isOpen": True,
            "hours": p.operating_hours or "24 Hours",
            "terminal": p.terminal or "",
            "floor": p.floor_name or "",
            "gate": p.gate or "",
            "distanceM": p.distance_m or 100,
            "image": p.image_url or "",
            "badge": p.badge_label or "",
            "badgeVariant": p.badge_variant or "purple",
            "filter": p.sub_category.split(",") if p.sub_category else []
        } for p in pois]

        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching directory POIs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.get("/api/v1/map/nodes")
async def get_map_nodes(db: Session = Depends(get_db)):
    """
    Loads spatial map nodes with attached POIs for frontend interactive map editor.
    """
    try:
        nodes = db.query(models.MapNode).options(joinedload(models.MapNode.pois)).all()
        frontend_nodes = []

        for node in nodes:
            node_data = {
                "id": node.id,
                "x": node.x_coord,
                "y": node.y_coord,
                "level": node.floor_id.replace("floor-", "").upper(),
            }

            if node.pois:
                poi = node.pois[0]
                node_data["label"] = poi.name
                node_data["type"] = poi.category.lower()
                cat = poi.category.lower()
                if "dining" in cat or "eat" in cat:
                    node_data["icon"] = "restaurant"
                elif "retail" in cat or "shopping" in cat:
                    node_data["icon"] = "storefront"
                elif "lounge" in cat:
                    node_data["icon"] = "weekend"
                elif "restroom" in cat:
                    node_data["icon"] = "wc"
                elif "medical" in cat:
                    node_data["icon"] = "local_hospital"
                elif "gate" in cat:
                    node_data["icon"] = "flight_takeoff"
                else:
                    node_data["icon"] = "place"
            elif node.is_vertical_connector:
                node_data["label"] = node.zone_name
                node_data["type"] = node.connector_type or "elevator"
                node_data["icon"] = "elevator" if node.connector_type == "elevator" else "escalator"
            else:
                node_data["label"] = node.zone_name
                node_data["type"] = "waypoint"
                node_data["icon"] = "circle"

            frontend_nodes.append(node_data)

        return {"success": True, "data": frontend_nodes}
    except Exception as e:
        logger.error(f"Error fetching map nodes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.post("/api/v1/map/nodes")
async def update_map_nodes(
    payload: MapNodeUpdatePayload,
    db: Session = Depends(get_db)
):
    """
    Bulk update coordinate positions for spatial map editor.
    """
    try:
        for n in payload.nodes:
            db_node = db.query(models.MapNode).filter(models.MapNode.id == n.id).first()
            if db_node:
                db_node.x_coord = float(n.x)
                db_node.y_coord = float(n.y)

        db.commit()
        return {"success": True, "message": "Nodes updated successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating map nodes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )
