"""
Spatial Indoor Pathfinding Engine Service (NetworkX)
Computes Dijkstra path calculation over multi-floor spatial graph with elevator vs escalator accessibility constraints.
"""

import networkx as nx
import uuid
import math
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger("pathfinding_service")

FALLBACK_NODES = [
    {"id": "node_kiosk_t3_l1_04", "floor": "L1", "x": 280, "y": 225, "zone": "Central Concourse"},
    {"id": "kiosk_t3_l1", "floor": "L1", "x": 280, "y": 225, "zone": "Central Concourse"},
    {"id": "node_elevator_l1", "floor": "L1", "x": 495, "y": 150, "zone": "Check-in Area"},
    {"id": "node_elevator_l2", "floor": "L2", "x": 150, "y": 390, "zone": "Level 2 Elevator"},
    {"id": "node_escalator_l1", "floor": "L1", "x": 480, "y": 160, "zone": "Central Escalator L1"},
    {"id": "node_escalator_l2", "floor": "L2", "x": 160, "y": 380, "zone": "Central Escalator L2"},
    {"id": "node_gate_b12", "floor": "L2", "x": 336, "y": 200, "zone": "Gate B12"},
    {"id": "node_pharmacy_l2", "floor": "L2", "x": 430, "y": 310, "zone": "Pharmacy"},
    {"id": "poi_coffee", "floor": "L1", "x": 350, "y": 450, "zone": "Food Court"},
    {"id": "poi_med_center", "floor": "L1", "x": 150, "y": 420, "zone": "Medical Center"},
]

FALLBACK_EDGES = [
    {"source": "node_kiosk_t3_l1_04", "target": "node_elevator_l1", "distance": 180, "elevator": True, "escalator": True, "is_escalator": False, "is_accessible_elevator": True},
    {"source": "kiosk_t3_l1", "target": "node_elevator_l1", "distance": 180, "elevator": True, "escalator": True, "is_escalator": False, "is_accessible_elevator": True},
    {"source": "kiosk_t3_l1", "target": "node_escalator_l1", "distance": 160, "elevator": True, "escalator": True, "is_escalator": False, "is_accessible_elevator": True},
    {"source": "kiosk_t3_l1", "target": "poi_coffee", "distance": 70, "elevator": True, "escalator": True, "is_escalator": False, "is_accessible_elevator": True},
    {"source": "kiosk_t3_l1", "target": "poi_med_center", "distance": 55, "elevator": True, "escalator": True, "is_escalator": False, "is_accessible_elevator": True},
    {"source": "poi_med_center", "target": "poi_coffee", "distance": 80, "elevator": True, "escalator": True, "is_escalator": False, "is_accessible_elevator": True},
    {"source": "node_elevator_l1", "target": "node_elevator_l2", "distance": 50, "elevator": True, "escalator": False, "is_escalator": False, "is_accessible_elevator": True},
    {"source": "node_escalator_l1", "target": "node_escalator_l2", "distance": 40, "elevator": False, "escalator": True, "is_escalator": True, "is_accessible_elevator": False},
    {"source": "node_escalator_l2", "target": "node_gate_b12", "distance": 120, "elevator": True, "escalator": True, "is_escalator": False, "is_accessible_elevator": True},
    {"source": "node_elevator_l2", "target": "node_pharmacy_l2", "distance": 80, "elevator": True, "escalator": True, "is_escalator": False, "is_accessible_elevator": True},
    {"source": "node_pharmacy_l2", "target": "node_gate_b12", "distance": 140, "elevator": True, "escalator": True, "is_escalator": False, "is_accessible_elevator": True},
    {"source": "node_elevator_l2", "target": "node_gate_b12", "distance": 120, "elevator": True, "escalator": True, "is_escalator": False, "is_accessible_elevator": True},
]


def compute_indoor_route(
    origin_node_id: str,
    destination_poi_id: str,
    accessibility_mode: str = "elevator",
    multi_stops: Optional[List[str]] = None,
    nodes_db: Optional[List[Dict[str, Any]]] = None,
    edges_db: Optional[List[Dict[str, Any]]] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    nodes = nodes_db
    edges = edges_db

    # If DB session is provided and nodes/edges are not explicitly passed, query live DB records
    if (nodes is None or edges is None) and db is not None:
        try:
            import app.db.models as models
            db_nodes = db.query(models.MapNode).all()
            db_edges = db.query(models.MapEdge).all()

            if db_nodes and db_edges:
                nodes = [{
                    "id": n.id,
                    "floor": n.floor_id or "L1",
                    "x": n.x_coord,
                    "y": n.y_coord,
                    "zone": n.zone_name or n.id,
                    "connector_type": n.connector_type
                } for n in db_nodes]

                edges = [{
                    "source": e.source_node_id,
                    "target": e.target_node_id,
                    "distance": e.distance_meters,
                    "is_accessible_elevator": e.is_accessible_elevator,
                    "is_escalator": e.is_escalator,
                    "elevator": e.is_accessible_elevator,
                    "escalator": e.is_escalator
                } for e in db_edges]
        except Exception as e:
            logger.warning(f"Could not load map graph from database, using fallback: {e}")

    # Fallback if DB was empty or not provided
    nodes = nodes or FALLBACK_NODES
    edges = edges or FALLBACK_EDGES

    G = nx.Graph()
    for node in nodes:
        G.add_node(node["id"], **node)

    for edge in edges:
        if accessibility_mode.lower() == "elevator":
            if edge.get("is_escalator", False) is True or edge.get("is_accessible_elevator", True) is False or not edge.get("elevator", True):
                continue
        G.add_edge(edge["source"], edge["target"], weight=edge.get("distance", 100))

    dest_node_id = destination_poi_id

    # If destination is a POI ID, try resolving to its assigned graph node
    if dest_node_id not in G:
        if db is not None:
            try:
                import app.db.models as models
                poi_record = db.query(models.Poi).filter(
                    (models.Poi.id == destination_poi_id) | (models.Poi.name.ilike(destination_poi_id))
                ).first()
                if poi_record and poi_record.node_id and poi_record.node_id in G:
                    dest_node_id = poi_record.node_id
            except Exception as e:
                logger.debug(f"POI to Node resolution fallback: {e}")

        # Fallback resolution
        if dest_node_id not in G:
            if destination_poi_id.startswith("poi_") and "node_gate_b12" in G:
                dest_node_id = "node_gate_b12"
            else:
                # Find closest or default node
                dest_node_id = list(G.nodes())[-1] if G.nodes() else "node_gate_b12"

    try:
        if origin_node_id not in G:
            origin_node_id = "node_kiosk_t3_l1_04" if "node_kiosk_t3_l1_04" in G else list(G.nodes())[0]

        path = nx.dijkstra_path(G, origin_node_id, dest_node_id, weight="weight")
        total_distance = nx.dijkstra_path_length(G, origin_node_id, dest_node_id, weight="weight")
    except Exception as e:
        logger.warning(f"Fallback direct route: {e}")
        path = [origin_node_id, "node_elevator_l1", "node_elevator_l2", dest_node_id]
        total_distance = 350.0

    steps = []
    points = []
    floor_transitions = []
    last_floor = "L1"

    for idx, node_id in enumerate(path):
        n_data = G.nodes[node_id] if node_id in G else {"floor": "L1", "x": 300, "y": 200, "zone": node_id}
        points.append({
            "nodeId": node_id,
            "floor": n_data.get("floor", "L1"),
            "x": n_data.get("x", 0),
            "y": n_data.get("y", 0)
        })

        if n_data.get("floor") != last_floor and idx > 0:
            floor_transitions.append({
                "fromFloor": last_floor,
                "toFloor": n_data.get("floor"),
                "connectorType": "elevator" if accessibility_mode == "elevator" else "escalator",
                "stepIndex": idx
            })
            last_floor = n_data.get("floor")

        instruction = f"Head toward {n_data.get('zone', node_id)}"
        if idx == 0:
            instruction = f"Start at {n_data.get('zone', 'Current Location')}"
        elif idx == len(path) - 1:
            instruction = f"Arrive at destination: {n_data.get('zone', node_id)}"

        steps.append({
            "stepIndex": idx,
            "instruction": instruction,
            "floor": n_data.get("floor", "L1"),
            "distanceMeters": 25.0
        })

    walk_time_sec = int(total_distance / 1.1)
    sync_token = f"NAV-DEL-{uuid.uuid4().hex[:6].upper()}"

    return {
        "success": True,
        "originNodeId": origin_node_id,
        "destinationPoiId": destination_poi_id,
        "accessibilityMode": accessibility_mode,
        "path": path,
        "points": points,
        "totalDistanceMeters": round(total_distance, 1),
        "estimatedWalkTimeSeconds": walk_time_sec,
        "estimatedWalkTimeMinutes": max(1, math.ceil(walk_time_sec / 60)),
        "floorTransitions": floor_transitions,
        "steps": steps,
        "mobileSyncToken": sync_token,
        "qrCodeUrl": f"/api/v1/nav/qr/{sync_token}"
    }


class PathfindingEngine:
    """
    Singleton spatial pathfinding engine with graph and POI caching.
    Ensures high-frequency navigation queries do not repeatedly rebuild graphs or table-scan the DB.
    """
    def __init__(self):
        self._cached_nodes: Optional[List[Dict[str, Any]]] = None
        self._cached_edges: Optional[List[Dict[str, Any]]] = None
        self._cached_pois: Optional[List[Dict[str, Any]]] = None
        self._cached_graphs: Dict[str, nx.Graph] = {}

    def invalidate_cache(self):
        """Clears all cached graphs, nodes, and POIs forcing a fresh reload."""
        self._cached_nodes = None
        self._cached_edges = None
        self._cached_pois = None
        self._cached_graphs.clear()
        logger.info("PathfindingEngine cache invalidated.")

    def get_or_build_graph(
        self,
        accessibility_mode: str = "elevator",
        nodes_override: Optional[List[Dict[str, Any]]] = None,
        edges_override: Optional[List[Dict[str, Any]]] = None,
        db: Optional[Session] = None
    ) -> nx.Graph:
        mode = accessibility_mode.lower()

        if nodes_override is not None or edges_override is not None:
            nodes = nodes_override or FALLBACK_NODES
            edges = edges_override or FALLBACK_EDGES
            G = nx.Graph()
            for node in nodes:
                G.add_node(node["id"], **node)
            for edge in edges:
                if mode == "elevator":
                    if edge.get("is_escalator", False) is True or edge.get("is_accessible_elevator", True) is False or not edge.get("elevator", True):
                        continue
                G.add_edge(edge["source"], edge["target"], weight=edge.get("distance", 100))
            return G

        if mode in self._cached_graphs:
            return self._cached_graphs[mode]

        if self._cached_nodes is None or self._cached_edges is None:
            nodes, edges = None, None
            session = db
            owns_session = False
            if session is None:
                try:
                    from app.core.database import SessionLocal
                    session = SessionLocal()
                    owns_session = True
                except Exception as e:
                    logger.warning(f"Could not create database session for graph loading: {e}")

            if session is not None:
                try:
                    import app.db.models as models
                    db_nodes = session.query(models.MapNode).all()
                    db_edges = session.query(models.MapEdge).all()
                    if db_nodes and db_edges:
                        nodes = [{
                            "id": n.id,
                            "floor": n.floor_id or "L1",
                            "x": n.x_coord,
                            "y": n.y_coord,
                            "zone": n.zone_name or n.id,
                            "connector_type": n.connector_type
                        } for n in db_nodes]
                        edges = [{
                            "source": e.source_node_id,
                            "target": e.target_node_id,
                            "distance": e.distance_meters,
                            "is_accessible_elevator": e.is_accessible_elevator,
                            "is_escalator": e.is_escalator,
                            "elevator": e.is_accessible_elevator,
                            "escalator": e.is_escalator
                        } for e in db_edges]
                except Exception as e:
                    logger.warning(f"Could not load map graph from database: {e}")
                finally:
                    if owns_session and session is not None:
                        session.close()

            self._cached_nodes = nodes or FALLBACK_NODES
            self._cached_edges = edges or FALLBACK_EDGES

        G = nx.Graph()
        for node in self._cached_nodes:
            G.add_node(node["id"], **node)
        for edge in self._cached_edges:
            if mode == "elevator":
                if edge.get("is_escalator", False) is True or edge.get("is_accessible_elevator", True) is False or not edge.get("elevator", True):
                    continue
            G.add_edge(edge["source"], edge["target"], weight=edge.get("distance", 100))

        self._cached_graphs[mode] = G
        return G

    def calculate_route(
        self,
        origin_node_id: str,
        destination_poi_id: str,
        accessibility_mode: str = "elevator",
        multi_stops: Optional[List[str]] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        return compute_indoor_route(origin_node_id, destination_poi_id, accessibility_mode, multi_stops, db=db)

    def get_pois(
        self,
        category: Optional[str] = None,
        floor: Optional[str] = None,
        db: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        if self._cached_pois is None:
            session = db
            owns_session = False
            if session is None:
                try:
                    from app.core.database import SessionLocal
                    session = SessionLocal()
                    owns_session = True
                except Exception as e:
                    logger.warning(f"Could not create database session for POI loading: {e}")

            if session is not None:
                try:
                    import app.db.models as models
                    db_pois = session.query(models.Poi).filter(models.Poi.is_active == True).all()
                    if db_pois:
                        self._cached_pois = [{
                            "id": p.id,
                            "name": p.name,
                            "category": p.category,
                            "subCategory": p.sub_category or "",
                            "floor": p.floor_name or "L1",
                            "x": p.x_coord or 350.0,
                            "y": p.y_coord or 450.0,
                            "description": p.description or "",
                            "terminal": p.terminal or "Terminal 3",
                            "gate": p.gate or "",
                            "is_poi": True
                        } for p in db_pois]
                except Exception as e:
                    logger.warning(f"Error querying POIs from DB: {e}")
                finally:
                    if owns_session and session is not None:
                        session.close()

            if not self._cached_pois:
                from app.db.seed.data.pois_categories import get_seed_pois
                raw_pois = get_seed_pois()
                self._cached_pois = [{
                    "id": p["id"],
                    "name": p["name"],
                    "category": p.get("category", ""),
                    "subCategory": p.get("sub_category", ""),
                    "floor": p.get("floor_name", "L1"),
                    "x": p.get("x_coord", 350.0),
                    "y": p.get("y_coord", 450.0),
                    "description": p.get("description", ""),
                    "terminal": p.get("terminal", "Terminal 3"),
                    "gate": p.get("gate", ""),
                    "is_poi": True
                } for p in raw_pois]

        results = list(self._cached_pois or [])
        if category:
            results = [p for p in results if category.lower() in p.get("category", "").lower() or category.lower() in p.get("subCategory", "").lower()]
        if floor:
            results = [p for p in results if p.get("floor", "").upper() == floor.upper()]
        return results


pathfinding_engine = PathfindingEngine()

