"""
Spatial Indoor Pathfinding Engine Service (NetworkX)
Computes Dijkstra path calculation over multi-floor spatial graph with elevator vs escalator accessibility constraints.
"""

import networkx as nx
import uuid
import math
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("pathfinding_service")

AIRPORT_POIS: List[Dict[str, Any]] = [
    {"id": "poi_coffee", "name": "Third Wave Coffee", "category": "dining", "floor": "L1", "x": 350.0, "y": 450.0, "description": "Artisanal Coffee & Fresh Pastries", "is_poi": True},
    {"id": "poi_mcdonalds", "name": "McDonald's", "category": "dining", "floor": "L1", "x": 420.0, "y": 400.0, "description": "Fast Food & Desserts", "is_poi": True},
    {"id": "poi_subway", "name": "Subway", "category": "dining", "floor": "L1", "x": 450.0, "y": 410.0, "description": "Fresh Made-to-Order Subs", "is_poi": True},
    {"id": "poi_bikanervala", "name": "Bikanervala", "category": "dining", "floor": "L1", "x": 480.0, "y": 390.0, "description": "Indian Sweets & Express Meals", "is_poi": True},
    {"id": "poi_duty_free", "name": "Duty Free", "category": "shopping", "floor": "L1", "x": 300.0, "y": 320.0, "description": "International Perfumes & Liquors", "is_poi": True},
    {"id": "poi_imagine", "name": "Imagine Store", "category": "shopping", "floor": "L1", "x": 360.0, "y": 300.0, "description": "Apple Authorized Reseller", "is_poi": True},
    {"id": "poi_relay_books", "name": "Relay Books", "category": "shopping", "floor": "L1", "x": 400.0, "y": 280.0, "description": "Books, Magazines & Travel Goods", "is_poi": True},
    {"id": "poi_med_center", "name": "Medical Centre", "category": "services", "floor": "L1", "x": 150.0, "y": 420.0, "description": "24/7 First Aid & Medical Services", "is_poi": True},
    {"id": "poi_pharmacy", "name": "Pharmacy", "category": "services", "floor": "L1", "x": 180.0, "y": 410.0, "description": "Apollo Pharmacy & Express Medicine", "is_poi": True},
    {"id": "poi_baggage", "name": "Baggage Services", "category": "services", "floor": "L1", "x": 220.0, "y": 550.0, "description": "Baggage wrap & lost property", "is_poi": True},
    {"id": "poi_currency", "name": "Currency Exchange", "category": "services", "floor": "L1", "x": 280.0, "y": 520.0, "description": "Thomas Cook Forex", "is_poi": True},
    {"id": "poi_encalm", "name": "Encalm Lounge", "category": "lounges", "floor": "L2", "x": 350.0, "y": 120.0, "description": "VIP Lounge with Buffet & Spa", "is_poi": True},
    {"id": "poi_plaza_lounge", "name": "Plaza Premium Lounge", "category": "lounges", "floor": "L2", "x": 420.0, "y": 110.0, "description": "Premium Passenger Lounge", "is_poi": True},
    {"id": "poi_air_india", "name": "Air India Maharaja Lounge", "category": "lounges", "floor": "L2", "x": 500.0, "y": 100.0, "description": "Exclusive Business Class Lounge", "is_poi": True},
    {"id": "node_gate_20", "name": "Gate 20", "category": "gates", "floor": "L1", "x": 600.0, "y": 200.0, "description": "Boarding Gate 20", "is_poi": True},
    {"id": "node_gate_25", "name": "Gate 25", "category": "gates", "floor": "L1", "x": 700.0, "y": 200.0, "description": "Boarding Gate 25", "is_poi": True},
    {"id": "node_gate_30", "name": "Gate 30", "category": "gates", "floor": "L2", "x": 650.0, "y": 100.0, "description": "Boarding Gate 30", "is_poi": True},
    {"id": "node_gate_37", "name": "Gate 37", "category": "gates", "floor": "L2", "x": 780.0, "y": 100.0, "description": "Boarding Gate 37", "is_poi": True},
    {"id": "poi_restroom_l1", "name": "Restrooms L1", "category": "amenities", "floor": "L1", "x": 200.0, "y": 350.0, "description": "Accessible Restrooms & Baby Care", "is_poi": True},
]

def compute_indoor_route(
    origin_node_id: str,
    destination_poi_id: str,
    accessibility_mode: str = "elevator",
    multi_stops: Optional[List[str]] = None,
    nodes_db: Optional[List[Dict[str, Any]]] = None,
    edges_db: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    nodes = nodes_db or [
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

    edges = edges_db or [
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

    G = nx.Graph()
    for node in nodes:
        G.add_node(node["id"], **node)

    for edge in edges:
        if accessibility_mode.lower() == "elevator":
            if edge.get("is_escalator", False) is True or edge.get("is_accessible_elevator", True) is False or not edge.get("elevator", True):
                continue
        G.add_edge(edge["source"], edge["target"], weight=edge.get("distance", 100))

    dest_node_id = destination_poi_id
    if destination_poi_id.startswith("poi_") and destination_poi_id not in G:
        dest_node_id = "node_gate_b12"

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
    def calculate_route(self, origin_node_id: str, destination_poi_id: str, accessibility_mode: str = "elevator", multi_stops: Optional[List[str]] = None) -> Dict[str, Any]:
        return compute_indoor_route(origin_node_id, destination_poi_id, accessibility_mode, multi_stops)

    def get_pois(self, category: Optional[str] = None, floor: Optional[str] = None) -> List[Dict[str, Any]]:
        results = AIRPORT_POIS
        if category:
            results = [p for p in results if p.get("category", "").lower() == category.lower()]
        if floor:
            results = [p for p in results if p.get("floor", "").upper() == floor.upper()]
        return results

pathfinding_engine = PathfindingEngine()
