"""
Seed Data Fixtures: Floors, Map Nodes, Map Edges & Kiosks
"""

def get_seed_floors():
    return [
        {"id": "floor-l1", "building": "Terminal 1", "floor_level": 1, "svg_asset_url": "/terminal1_level1_map.svg"},
        {"id": "floor-l2", "building": "Terminal 1", "floor_level": 2, "svg_asset_url": "/terminal1_level2_map.svg"},
        {"id": "floor-l3", "building": "Terminal 1", "floor_level": 3, "svg_asset_url": "/terminal1_level3_map.svg"},
    ]

def get_seed_map_nodes():
    return [
        # Level 1 Nodes
        {"id": "kiosk", "floor_id": "floor-l1", "x_coord": 1200.0, "y_coord": 1280.0, "zone_name": "Main Entrance Kiosk (E1)", "is_vertical_connector": False, "connector_type": None},
        {"id": "entrance_e1", "floor_id": "floor-l1", "x_coord": 1200.0, "y_coord": 1200.0, "zone_name": "Terminal Main Entrance E1", "is_vertical_connector": False, "connector_type": None},
        {"id": "info_desk", "floor_id": "floor-l1", "x_coord": 1200.0, "y_coord": 590.0, "zone_name": "Central Information Desk D01", "is_vertical_connector": False, "connector_type": None},
        {"id": "elevator_l01", "floor_id": "floor-l1", "x_coord": 815.0, "y_coord": 860.0, "zone_name": "Elevator L01 (West)", "is_vertical_connector": True, "connector_type": "elevator"},
        {"id": "elevator_l02", "floor_id": "floor-l1", "x_coord": 1535.0, "y_coord": 860.0, "zone_name": "Elevator L02 (East)", "is_vertical_connector": True, "connector_type": "elevator"},
        {"id": "escalator_e01_e02", "floor_id": "floor-l1", "x_coord": 805.0, "y_coord": 635.0, "zone_name": "Escalator E01/E02 (West)", "is_vertical_connector": True, "connector_type": "escalator"},
        {"id": "escalator_e03_e04", "floor_id": "floor-l1", "x_coord": 1505.0, "y_coord": 635.0, "zone_name": "Escalator E03/E04 (East)", "is_vertical_connector": True, "connector_type": "escalator"},

        # Level 2 Nodes
        {"id": "elevator_l01_l2", "floor_id": "floor-l2", "x_coord": 1100.0, "y_coord": 710.0, "zone_name": "Elevator L01 (Concourse)", "is_vertical_connector": True, "connector_type": "elevator"},
        {"id": "elevator_l02_l2", "floor_id": "floor-l2", "x_coord": 1250.0, "y_coord": 710.0, "zone_name": "Elevator L02 (Concourse)", "is_vertical_connector": True, "connector_type": "elevator"},
        {"id": "escalator_e01_l2", "floor_id": "floor-l2", "x_coord": 857.0, "y_coord": 295.0, "zone_name": "Escalator E01/E02 (Concourse)", "is_vertical_connector": True, "connector_type": "escalator"},
        {"id": "escalator_e03_l2", "floor_id": "floor-l2", "x_coord": 1542.0, "y_coord": 295.0, "zone_name": "Escalator E03/E04 (Concourse)", "is_vertical_connector": True, "connector_type": "escalator"},
        {"id": "security_sec04", "floor_id": "floor-l2", "x_coord": 920.0, "y_coord": 440.0, "zone_name": "Security Checkpoint (SEC04)", "is_vertical_connector": False, "connector_type": None},
        {"id": "gate_28", "floor_id": "floor-l2", "x_coord": 1770.0, "y_coord": 100.0, "zone_name": "Boarding Gate 28", "is_vertical_connector": False, "connector_type": None},
        {"id": "starbucks_c201", "floor_id": "floor-l2", "x_coord": 180.0, "y_coord": 620.0, "zone_name": "Starbucks Concourse (C201)", "is_vertical_connector": False, "connector_type": None},
        {"id": "mac_r201", "floor_id": "floor-l2", "x_coord": 360.0, "y_coord": 295.0, "zone_name": "MAC Cosmetics (R201)", "is_vertical_connector": False, "connector_type": None},
        {"id": "tumi_r206", "floor_id": "floor-l2", "x_coord": 2010.0, "y_coord": 295.0, "zone_name": "TUMI Store (R206)", "is_vertical_connector": False, "connector_type": None},

        # Level 3 Nodes
        {"id": "elevator_l03_l04_l3", "floor_id": "floor-l3", "x_coord": 1180.0, "y_coord": 45.0, "zone_name": "Elevators L03/L04 (Mezzanine)", "is_vertical_connector": True, "connector_type": "elevator"},
        {"id": "escalator_e01_l3", "floor_id": "floor-l3", "x_coord": 770.0, "y_coord": 420.0, "zone_name": "Escalator E01/E02 (Mezzanine)", "is_vertical_connector": True, "connector_type": "escalator"},
        {"id": "plaza_premium_l301", "floor_id": "floor-l3", "x_coord": 480.0, "y_coord": 385.0, "zone_name": "Plaza Premium Lounge (L301)", "is_vertical_connector": False, "connector_type": None},
        {"id": "adani_lounge_l302", "floor_id": "floor-l3", "x_coord": 480.0, "y_coord": 530.0, "zone_name": "Adani Lounge (L302)", "is_vertical_connector": False, "connector_type": None},
        {"id": "tata_lounge_l303", "floor_id": "floor-l3", "x_coord": 1920.0, "y_coord": 385.0, "zone_name": "Tata Lounge (L303)", "is_vertical_connector": False, "connector_type": None},
        {"id": "observation_deck_od301", "floor_id": "floor-l3", "x_coord": 1200.0, "y_coord": 885.0, "zone_name": "Observation Deck (OD301)", "is_vertical_connector": False, "connector_type": None},
        {"id": "gate_41", "floor_id": "floor-l3", "x_coord": 380.0, "y_coord": 100.0, "zone_name": "Boarding Gate 41", "is_vertical_connector": False, "connector_type": None},
    ]

def get_seed_map_edges():
    return [
        # L1 Edges
        {"id": "edge_01", "source_node_id": "kiosk", "target_node_id": "entrance_e1", "distance_meters": 10.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_02", "source_node_id": "entrance_e1", "target_node_id": "info_desk", "distance_meters": 45.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_03", "source_node_id": "entrance_e1", "target_node_id": "elevator_l01", "distance_meters": 35.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_04", "source_node_id": "entrance_e1", "target_node_id": "escalator_e01_e02", "distance_meters": 38.0, "is_accessible_elevator": False, "is_escalator": True},

        # Vertical Connections L1 <-> L2
        {"id": "edge_v_l1_l2_elev", "source_node_id": "elevator_l01", "target_node_id": "elevator_l01_l2", "distance_meters": 8.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_v_l1_l2_escl", "source_node_id": "escalator_e01_e02", "target_node_id": "escalator_e01_l2", "distance_meters": 12.0, "is_accessible_elevator": False, "is_escalator": True},

        # L2 Edges
        {"id": "edge_05", "source_node_id": "escalator_e01_l2", "target_node_id": "security_sec04", "distance_meters": 15.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_06", "source_node_id": "security_sec04", "target_node_id": "gate_28", "distance_meters": 55.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_07", "source_node_id": "security_sec04", "target_node_id": "starbucks_c201", "distance_meters": 30.0, "is_accessible_elevator": True, "is_escalator": False},

        # Vertical Connections L2 <-> L3
        {"id": "edge_v_l2_l3_escl", "source_node_id": "escalator_e01_l2", "target_node_id": "escalator_e01_l3", "distance_meters": 12.0, "is_accessible_elevator": False, "is_escalator": True},

        # L3 Edges
        {"id": "edge_08", "source_node_id": "escalator_e01_l3", "target_node_id": "plaza_premium_l301", "distance_meters": 20.0, "is_accessible_elevator": True, "is_escalator": False},
        {"id": "edge_09", "source_node_id": "escalator_e01_l3", "target_node_id": "observation_deck_od301", "distance_meters": 45.0, "is_accessible_elevator": True, "is_escalator": False},
    ]

def get_seed_kiosks():
    return [
        {
            "id": "T1-L1-K01",
            "code": "T1-L1-K01",
            "terminal": "Terminal 1",
            "floor_id": "floor-l1",
            "current_node_id": "kiosk",
            "is_accessible_ada": True,
            "status": "active"
        }
    ]

