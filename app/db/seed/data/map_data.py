"""
Seed Data Fixtures: Floors, Map Nodes, Map Edges & Kiosks
"""

def get_seed_floors():
    return [
        {"id": "floor-l1", "building": "Terminal 3 Concourse", "floor_level": 1, "svg_asset_url": "/maps/t3_level_1.svg"},
        {"id": "floor-l2", "building": "Terminal 3 Concourse", "floor_level": 2, "svg_asset_url": "/maps/t3_level_2.svg"}
    ]

def get_seed_map_nodes():
    return [
        # Level 1 Nodes
        {"id": "node_kiosk_t3_l1_04", "floor_id": "floor-l1", "x_coord": 350.0, "y_coord": 450.0, "zone_name": "Kiosk Zone Level 1", "is_vertical_connector": False, "connector_type": None},
        {"id": "node_security_exit_l1", "floor_id": "floor-l1", "x_coord": 400.0, "y_coord": 420.0, "zone_name": "Security Check Exit", "is_vertical_connector": False, "connector_type": None},
        {"id": "node_central_junction_l1", "floor_id": "floor-l1", "x_coord": 500.0, "y_coord": 400.0, "zone_name": "Central Concourse Hub L1", "is_vertical_connector": False, "connector_type": None},
        {"id": "node_retail_corridor_l1", "floor_id": "floor-l1", "x_coord": 600.0, "y_coord": 380.0, "zone_name": "Duty Free Retail Corridor", "is_vertical_connector": False, "connector_type": None},
        {"id": "node_poi_third_wave", "floor_id": "floor-l1", "x_coord": 650.0, "y_coord": 350.0, "zone_name": "Third Wave Coffee", "is_vertical_connector": False, "connector_type": None},
        {"id": "node_poi_relay_books", "floor_id": "floor-l1", "x_coord": 620.0, "y_coord": 440.0, "zone_name": "Relay Books Store", "is_vertical_connector": False, "connector_type": None},
        {"id": "node_elevator_bank_a_l1", "floor_id": "floor-l1", "x_coord": 520.0, "y_coord": 480.0, "zone_name": "Elevator Core A (L1)", "is_vertical_connector": True, "connector_type": "elevator"},
        {"id": "node_escalator_bank_a_l1", "floor_id": "floor-l1", "x_coord": 480.0, "y_coord": 480.0, "zone_name": "Escalator Core A (L1)", "is_vertical_connector": True, "connector_type": "escalator"},

        # Level 2 Nodes
        {"id": "node_elevator_bank_a_l2", "floor_id": "floor-l2", "x_coord": 520.0, "y_coord": 480.0, "zone_name": "Elevator Core A (L2)", "is_vertical_connector": True, "connector_type": "elevator"},
        {"id": "node_escalator_bank_a_l2", "floor_id": "floor-l2", "x_coord": 480.0, "y_coord": 480.0, "zone_name": "Escalator Core A (L2)", "is_vertical_connector": True, "connector_type": "escalator"},
        {"id": "node_central_junction_l2", "floor_id": "floor-l2", "x_coord": 500.0, "y_coord": 400.0, "zone_name": "Central Concourse Hub L2", "is_vertical_connector": False, "connector_type": None},
        {"id": "node_gate_b_corridor_l2", "floor_id": "floor-l2", "x_coord": 400.0, "y_coord": 300.0, "zone_name": "Gate B Pier Corridor", "is_vertical_connector": False, "connector_type": None},
        {"id": "node_gate_b12_l2", "floor_id": "floor-l2", "x_coord": 320.0, "y_coord": 250.0, "zone_name": "Departure Gate B12", "is_vertical_connector": False, "connector_type": None},
        {"id": "node_poi_medical_l2", "floor_id": "floor-l2", "x_coord": 450.0, "y_coord": 280.0, "zone_name": "Medical Center & Pharmacy", "is_vertical_connector": False, "connector_type": None},
        {"id": "node_poi_encalm_l2", "floor_id": "floor-l2", "x_coord": 600.0, "y_coord": 300.0, "zone_name": "Encalm Lounge Entrance", "is_vertical_connector": False, "connector_type": None},
    ]

def get_seed_map_edges():
    return [
        # L1 Horizontal Edges
        {"id": "edge_01", "source_node_id": "node_kiosk_t3_l1_04", "target_node_id": "node_security_exit_l1", "distance_meters": 18.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_02", "source_node_id": "node_security_exit_l1", "target_node_id": "node_central_junction_l1", "distance_meters": 22.5, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_03", "source_node_id": "node_central_junction_l1", "target_node_id": "node_retail_corridor_l1", "distance_meters": 25.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_04", "source_node_id": "node_retail_corridor_l1", "target_node_id": "node_poi_third_wave", "distance_meters": 14.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_05", "source_node_id": "node_retail_corridor_l1", "target_node_id": "node_poi_relay_books", "distance_meters": 16.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_06", "source_node_id": "node_central_junction_l1", "target_node_id": "node_elevator_bank_a_l1", "distance_meters": 12.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_07", "source_node_id": "node_central_junction_l1", "target_node_id": "node_escalator_bank_a_l1", "distance_meters": 10.0, "is_accessible_elevator": True, "is_escalator": False},

        # Vertical Connections between L1 and L2
        {"id": "edge_vert_elevator", "source_node_id": "node_elevator_bank_a_l1", "target_node_id": "node_elevator_bank_a_l2", "distance_meters": 8.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_vert_escalator", "source_node_id": "node_escalator_bank_a_l1", "target_node_id": "node_escalator_bank_a_l2", "distance_meters": 12.0, "is_accessible_elevator": False, "is_escalator": True},

        # L2 Horizontal Edges
        {"id": "edge_08", "source_node_id": "node_elevator_bank_a_l2", "target_node_id": "node_central_junction_l2", "distance_meters": 12.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_09", "source_node_id": "node_escalator_bank_a_l2", "target_node_id": "node_central_junction_l2", "distance_meters": 10.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_10", "source_node_id": "node_central_junction_l2", "target_node_id": "node_gate_b_corridor_l2", "distance_meters": 35.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_11", "source_node_id": "node_gate_b_corridor_l2", "target_node_id": "node_gate_b12_l2", "distance_meters": 28.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_12", "source_node_id": "node_gate_b_corridor_l2", "target_node_id": "node_poi_medical_l2", "distance_meters": 15.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_13", "source_node_id": "node_central_junction_l2", "target_node_id": "node_poi_encalm_l2", "distance_meters": 32.0, "is_accessible_elevator": True, "is_escalator": False},
    ]

def get_seed_kiosks():
    return [
        {
            "id": "T3-L1-K04",
            "code": "T3-L1-K04",
            "terminal": "Terminal 3",
            "floor_id": "floor-l1",
            "current_node_id": "node_kiosk_t3_l1_04",
            "is_accessible_ada": True,
            "status": "active"
        }
    ]
