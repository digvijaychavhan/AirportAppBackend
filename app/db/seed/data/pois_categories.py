"""
Seed Data Fixtures: Points of Interest (POIs) & Wayfinding Categories
"""

def get_seed_categories():
    return [
        {
            "id": "shopping",
            "title": "Shopping",
            "description": "Explore shops and\nretail stores",
            "photo_url": "/findway-shopping.png",
            "icon": "shopping_bag",
            "icon_color": "#2563EB",
            "icon_bg": "#DBEAFE",
            "route": "/wayfinding/shopping",
        },
        {
            "id": "dining",
            "title": "Eat & Dine",
            "description": "Restaurants, cafes\nand fast food",
            "photo_url": "/findway-dining.png",
            "icon": "restaurant",
            "icon_color": "#D97706",
            "icon_bg": "#FEF3C7",
            "route": "/eat-dine",
        },
        {
            "id": "services",
            "title": "Services",
            "description": "Assistance, counters\nand other services",
            "photo_url": "/findway-services.png",
            "icon": "support_agent",
            "icon_color": "#7C3AED",
            "icon_bg": "#EDE9FE",
            "route": "/wayfinding/services",
        },
        {
            "id": "gates",
            "title": "Boarding Gates",
            "description": "Find your boarding gates\nand directions",
            "photo_url": "/findway-gates.png",
            "icon": "flight_takeoff",
            "icon_color": "#059669",
            "icon_bg": "#D1FAE5",
            "route": "/wayfinding/gates",
        },
        {
            "id": "lounges",
            "title": "Lounges",
            "description": "Airport lounges and\nrelaxation areas",
            "photo_url": "/findway-lounge.png",
            "icon": "weekend",
            "icon_color": "#DB2777",
            "icon_bg": "#FCE7F3",
            "route": "/wayfinding/lounges",
        },
        {
            "id": "amenities",
            "title": "Airport Amenities",
            "description": "Facilities like restrooms,\nprayer rooms and more",
            "photo_url": "/findway-amenities.png",
            "icon": "wc",
            "icon_color": "#0891B2",
            "icon_bg": "#CFFAFE",
            "route": "/wayfinding/amenities",
        },
    ]

def get_seed_pois():
    return [
        # Dining / Eat & Dine
        {
            "id": "poi_r1", "name": "Third Wave Coffee", "category": "eat-dine", "sub_category": "cafe",
            "description": "Specialty coffee, pastries, sandwiches & more", "operating_hours": "6:00 AM – 11:00 PM",
            "terminal": "T3 Departure", "floor_name": "Level 2", "gate": "Near Gate 24", "distance_m": 120,
            "node_id": "node_poi_third_wave", "floor_id": "floor-l1",
            "image_url": "/restaurants/third-wave-coffee.png", "x_coord": 650.0, "y_coord": 350.0
        },
        {
            "id": "poi_r2", "name": "McDonald's", "category": "eat-dine", "sub_category": "fastfood",
            "description": "Burgers, fries, beverages and more", "operating_hours": "24 Hours",
            "terminal": "T3 Departure", "floor_name": "Food Court", "gate": "", "distance_m": 150,
            "image_url": "/restaurants/mcdonalds.png", "x_coord": 580.0, "y_coord": 330.0
        },
        {
            "id": "poi_r3", "name": "Bikanervala", "category": "eat-dine", "sub_category": "indian",
            "description": "North Indian snacks, meals & sweets", "operating_hours": "6:00 AM – 11:00 PM",
            "terminal": "T3 Departure", "floor_name": "", "gate": "Near Gate 19", "distance_m": 180,
            "image_url": "/restaurants/bikanervala.png", "x_coord": 520.0, "y_coord": 310.0
        },
        {
            "id": "poi_r4", "name": "Subway", "category": "eat-dine", "sub_category": "fastfood",
            "description": "Sandwiches, salads & wraps", "operating_hours": "6:00 AM – 12:00 AM",
            "terminal": "T3 Departure", "floor_name": "Food Court", "gate": "", "distance_m": 210,
            "image_url": "/restaurants/subway.png", "x_coord": 610.0, "y_coord": 360.0
        },
        {
            "id": "poi_r5", "name": "Sichuan House", "category": "eat-dine", "sub_category": "asian",
            "description": "Chinese cuisine, noodles & rice", "operating_hours": "11:00 AM – 11:00 PM",
            "terminal": "T3 Departure", "floor_name": "", "gate": "Near Gate 32", "distance_m": 260,
            "image_url": "/restaurants/sichuan-house.png", "x_coord": 560.0, "y_coord": 290.0
        },

        # Shopping
        {
            "id": "poi_s1", "name": "Duty Free", "category": "shopping", "sub_category": "dutyfree",
            "description": "Luxury perfumes, cosmetics, chocolates, liquor and travel exclusives.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 18",
            "distance_m": 110, "image_url": "/shopping/duty-free.png", "x_coord": 600.0, "y_coord": 380.0
        },
        {
            "id": "poi_s2", "name": "Imagine Store", "category": "shopping", "sub_category": "electronics",
            "description": "Apple products, accessories and premium electronics.",
            "operating_hours": "06:00 AM – 11:00 PM", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 22",
            "distance_m": 150, "image_url": "/shopping/imagine-store.png", "x_coord": 630.0, "y_coord": 400.0
        },
        {
            "id": "poi_s3", "name": "Hidesign", "category": "shopping", "sub_category": "fashion",
            "description": "Leather bags, wallets, backpacks and travel accessories.",
            "operating_hours": "08:00 AM – 10:00 PM", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 30",
            "distance_m": 190, "image_url": "/shopping/hidesign.png", "x_coord": 590.0, "y_coord": 420.0
        },
        {
            "id": "poi_s4", "name": "Relay Books", "category": "shopping", "sub_category": "books",
            "description": "Books, magazines, snacks and travel accessories.",
            "operating_hours": "05:00 AM – 11:00 PM", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 11",
            "distance_m": 220, "image_url": "/shopping/relay-books.png", "node_id": "node_poi_relay_books",
            "floor_id": "floor-l1", "x_coord": 620.0, "y_coord": 440.0
        },

        # Lounges
        {
            "id": "poi_l1", "name": "Encalm Lounge", "category": "lounge", "sub_category": "t3,international,24hr,premium",
            "description": "Premium lounge offering gourmet dining, Wi-Fi, shower facilities and business workstations.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Near Gate 15",
            "distance_m": 120, "image_url": "/lounges/encalm-lounge.png", "badge_label": "Premium", "badge_variant": "purple",
            "node_id": "node_poi_encalm_l2", "floor_id": "floor-l2", "x_coord": 600.0, "y_coord": 300.0
        },
        {
            "id": "poi_l2", "name": "Plaza Premium Lounge", "category": "lounge", "sub_category": "t3,international,24hr,business",
            "description": "International lounge with buffet, shower rooms and dedicated business zone.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "International Departures",
            "distance_m": 180, "image_url": "/lounges/plaza-premium.png", "badge_label": "International", "badge_variant": "teal",
            "x_coord": 620.0, "y_coord": 270.0
        },

        # Amenities & Gates
        {
            "id": "poi_gate_b12", "name": "Gate B12", "category": "gates", "sub_category": "domestic_gate",
            "description": "Departure Gate B12 - Boarding Concourse Level 2", "operating_hours": "24 Hours",
            "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Gate B12", "distance_m": 95,
            "node_id": "node_gate_b12_l2", "floor_id": "floor-l2", "x_coord": 320.0, "y_coord": 250.0
        },
        {
            "id": "poi_medical_centre", "name": "Medical Centre & Pharmacy", "category": "amenities", "sub_category": "health",
            "description": "24/7 First Aid, Emergency Doctor, and Travel Pharmacy", "operating_hours": "24 Hours",
            "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Near Gate B12", "distance_m": 80,
            "node_id": "node_poi_medical_l2", "floor_id": "floor-l2", "x_coord": 450.0, "y_coord": 280.0
        }
    ]
