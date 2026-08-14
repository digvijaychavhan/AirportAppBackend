import json
import logging
from starlette.responses import JSONResponse
from starlette.routing import Route
from database import SessionLocal
from models import MapNode, Poi, MapFloor
from sqlalchemy.orm import joinedload

logger = logging.getLogger("map_editor")

async def get_map_nodes(request):
    try:
        db = SessionLocal()
        # Ensure we load POIs with the nodes to build the frontend structure
        nodes = db.query(MapNode).options(joinedload(MapNode.pois)).all()
        
        frontend_nodes = []
        for node in nodes:
            # Map database schema to frontend AIRPORT_NODES schema
            node_data = {
                "id": node.id,
                "x": node.x_coord,
                "y": node.y_coord,
                "level": node.floor_id.replace("floor-", "").upper(), # e.g. "floor-l1" -> "L1"
            }
            
            # If the node has a POI attached, it's a specific amenity/store
            if node.pois:
                poi = node.pois[0] # Assume 1 POI per node for now
                node_data["label"] = poi.name
                node_data["type"] = poi.category.lower()
                # Simple icon mapping based on category
                cat = poi.category.lower()
                if "dining" in cat: node_data["icon"] = "restaurant"
                elif "retail" in cat or "shopping" in cat: node_data["icon"] = "storefront"
                elif "lounge" in cat: node_data["icon"] = "weekend"
                elif "restroom" in cat: node_data["icon"] = "wc"
                elif "medical" in cat: node_data["icon"] = "local_hospital"
                elif "gate" in cat: node_data["icon"] = "flight_takeoff"
                else: node_data["icon"] = "place"
            elif node.is_vertical_connector:
                node_data["label"] = node.zone_name
                node_data["type"] = node.connector_type or "elevator"
                node_data["icon"] = "elevator" if node.connector_type == "elevator" else "escalator"
            else:
                node_data["label"] = node.zone_name
                node_data["type"] = "waypoint"
                node_data["icon"] = "circle"
                
            frontend_nodes.append(node_data)
            
        db.close()
        
        # If DB is empty, return an empty array (the frontend handles fallback)
        return JSONResponse({"success": True, "data": frontend_nodes})
    except Exception as e:
        logger.error(f"Error fetching map nodes: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

async def update_map_nodes(request):
    try:
        body = await request.json()
        nodes_payload = body.get("nodes", [])
        
        db = SessionLocal()
        
        # Very simple bulk update strategy for coordinates
        for n in nodes_payload:
            node_id = n.get("id")
            if not node_id: continue
            
            db_node = db.query(MapNode).filter(MapNode.id == node_id).first()
            if db_node:
                db_node.x_coord = float(n.get("x", db_node.x_coord))
                db_node.y_coord = float(n.get("y", db_node.y_coord))
        
        db.commit()
        db.close()
        return JSONResponse({"success": True, "message": "Nodes updated successfully"})
    except Exception as e:
        logger.error(f"Error updating map nodes: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

routes = [
    Route("/api/v1/map/nodes", get_map_nodes, methods=["GET"]),
    Route("/api/v1/map/nodes", update_map_nodes, methods=["POST"])
]
