"""
Seed Data Fixtures: Points of Interest (POIs) & Wayfinding Categories
"""
import json

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
            "subcategories_json": json.dumps([
                {"id": "dutyfree", "label": "Duty Free", "icon": "local_airport"},
                {"id": "electronics", "label": "Electronics", "icon": "devices"},
                {"id": "fashion", "label": "Fashion", "icon": "checkroom"},
                {"id": "luxury", "label": "Luxury", "icon": "diamond"},
                {"id": "books", "label": "Books", "icon": "menu_book"},
                {"id": "beauty", "label": "Beauty", "icon": "spa"},
                {"id": "convenience", "label": "Convenience", "icon": "storefront"},
                {"id": "jewellery", "label": "Jewellery", "icon": "diamond"},
                {"id": "accessories", "label": "Accessories", "icon": "watch"}
            ])
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
            "subcategories_json": json.dumps([
                {"id": "cafe", "label": "Cafe & Coffee", "icon": "local_cafe"},
                {"id": "fastfood", "label": "Fast Food", "icon": "lunch_dining"},
                {"id": "indian", "label": "Indian", "icon": "restaurant"},
                {"id": "asian", "label": "Asian", "icon": "ramen_dining"},
                {"id": "desserts", "label": "Desserts", "icon": "icecream"},
                {"id": "healthy", "label": "Healthy", "icon": "eco"},
                {"id": "bar", "label": "Bar & Drinks", "icon": "local_bar"}
            ])
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
            "subcategories_json": json.dumps([
                {"id": "assistance", "label": "Information & Help", "icon": "info"},
                {"id": "financial", "label": "Forex & ATM", "icon": "currency_exchange"},
                {"id": "medical", "label": "Medical Centre", "icon": "medical_services"},
                {"id": "baggage", "label": "Left Luggage & Wrap", "icon": "luggage"},
                {"id": "telecom", "label": "SIM & Telecom", "icon": "sim_card"},
                {"id": "transport", "label": "Taxi & Car Rental", "icon": "local_taxi"}
            ])
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
            "subcategories_json": json.dumps([
                {"id": "t1", "label": "Terminal 1", "icon": "business"},
                {"id": "t2", "label": "Terminal 2", "icon": "business"},
                {"id": "t3", "label": "Terminal 3", "icon": "business"},
                {"id": "domestic", "label": "Domestic Concourse", "icon": "flight_land"},
                {"id": "international", "label": "International Concourse", "icon": "flight_takeoff"}
            ])
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
            "subcategories_json": json.dumps([
                {"id": "t1", "label": "Terminal 1", "icon": "business"},
                {"id": "t2", "label": "Terminal 2", "icon": "business"},
                {"id": "t3", "label": "Terminal 3", "icon": "business"},
                {"id": "domestic", "label": "Domestic", "icon": "flight_land"},
                {"id": "international", "label": "International", "icon": "flight_takeoff"},
                {"id": "24hr", "label": "24 Hours", "icon": "schedule"},
                {"id": "premium", "label": "Premium", "icon": "stars"},
                {"id": "business", "label": "Business", "icon": "work"}
            ])
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
            "subcategories_json": json.dumps([
                {"id": "restroom", "label": "Restrooms", "icon": "wc"},
                {"id": "water", "label": "Drinking Water", "icon": "water_drop"},
                {"id": "prayer", "label": "Prayer Room", "icon": "temple_hindu"},
                {"id": "babycare", "label": "Baby Care & Nursery", "icon": "child_care"},
                {"id": "smoking", "label": "Smoking Lounge", "icon": "smoking_rooms"},
                {"id": "charging", "label": "Charging Station", "icon": "power"},
                {"id": "trolley", "label": "Luggage Trolleys", "icon": "shopping_cart"}
            ])
        },
    ]

def get_seed_pois():
    return [
        # --- Dining / Eat & Dine ---
        {
            "id": "poi_r1", "name": "Third Wave Coffee", "category": "dining", "sub_category": "cafe",
            "description": "Specialty coffee, artisanal pastries, sandwiches & fresh brew", "operating_hours": "06:00 AM – 11:00 PM",
            "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Near Gate 24", "distance_m": 120,
            "badge_label": "Popular", "badge_variant": "amber",
            "image_url": "/restaurants/third-wave-coffee.png", "x_coord": 650.0, "y_coord": 350.0
        },
        {
            "id": "poi_r2", "name": "McDonald's", "category": "dining", "sub_category": "fastfood",
            "description": "Burgers, fries, beverages, breakfast items and happy meals", "operating_hours": "24 Hours",
            "terminal": "Terminal 3", "floor_name": "Food Court", "gate": "Near Security Exit", "distance_m": 150,
            "badge_label": "24/7", "badge_variant": "teal",
            "image_url": "/restaurants/mcdonalds.png", "x_coord": 580.0, "y_coord": 330.0
        },
        {
            "id": "poi_r3", "name": "Bikanervala", "category": "dining", "sub_category": "indian",
            "description": "Authentic North Indian thalis, street food snacks, chaat & traditional sweets", "operating_hours": "06:00 AM – 11:00 PM",
            "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 19", "distance_m": 180,
            "badge_label": "Indian", "badge_variant": "purple",
            "image_url": "/restaurants/bikanervala.png", "x_coord": 520.0, "y_coord": 310.0
        },
        {
            "id": "poi_r4", "name": "Subway", "category": "dining", "sub_category": "fastfood",
            "description": "Fresh customized subs, salads, wraps and cookies", "operating_hours": "06:00 AM – 12:00 AM",
            "terminal": "Terminal 3", "floor_name": "Food Court", "gate": "Near Food Court Entry", "distance_m": 210,
            "image_url": "/restaurants/subway.png", "x_coord": 610.0, "y_coord": 360.0
        },
        {
            "id": "poi_r5", "name": "Sichuan House", "category": "dining", "sub_category": "asian",
            "description": "Authentic Chinese cuisine, dim sums, noodles & wok specials", "operating_hours": "11:00 AM – 11:00 PM",
            "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Near Gate 32", "distance_m": 260,
            "image_url": "/restaurants/sichuan-house.png", "x_coord": 560.0, "y_coord": 290.0
        },
        {
            "id": "poi_r6", "name": "Starbucks Coffee", "category": "dining", "sub_category": "cafe",
            "description": "Espresso, frappuccinos, artisan bakery and grab-and-go meals", "operating_hours": "24 Hours",
            "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 14", "distance_m": 90,
            "badge_label": "24/7", "badge_variant": "teal",
            "image_url": "/restaurants/starbucks.png", "x_coord": 640.0, "y_coord": 320.0
        },

        # --- Shopping ---
        {
            "id": "poi_s1", "name": "Delhi Duty Free", "category": "shopping", "sub_category": "dutyfree",
            "description": "Luxury perfumes, cosmetics, chocolates, liquor and travel exclusives.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 18",
            "distance_m": 110, "badge_label": "Tax Free", "badge_variant": "teal",
            "image_url": "/shopping/duty-free.png", "x_coord": 600.0, "y_coord": 380.0
        },
        {
            "id": "poi_s2", "name": "Imagine Store (Apple)", "category": "shopping", "sub_category": "electronics",
            "description": "Apple devices, premium headphones, chargers, adapters and audio gear.",
            "operating_hours": "06:00 AM – 11:00 PM", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 22",
            "distance_m": 150, "image_url": "/shopping/imagine-store.png", "x_coord": 630.0, "y_coord": 400.0
        },
        {
            "id": "poi_s3", "name": "Hidesign", "category": "shopping", "sub_category": "fashion",
            "description": "Handcrafted leather bags, wallets, belts, backpacks and travel accessories.",
            "operating_hours": "08:00 AM – 10:00 PM", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 30",
            "distance_m": 190, "image_url": "/shopping/hidesign.png", "x_coord": 590.0, "y_coord": 420.0
        },
        {
            "id": "poi_s4", "name": "Relay Books & News", "category": "shopping", "sub_category": "books",
            "description": "Bestselling books, international magazines, travel gadgets and confectionery.",
            "operating_hours": "05:00 AM – 11:00 PM", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 11",
            "distance_m": 220, "image_url": "/shopping/relay-books.png", "x_coord": 620.0, "y_coord": 440.0
        },
        {
            "id": "poi_s5", "name": "Travel Essentials & Pharmacy", "category": "shopping", "sub_category": "convenience",
            "description": "Travel pillows, toiletries, snacks, OTC medicine, and emergency supplies.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Security Exit",
            "distance_m": 250, "badge_label": "24/7", "badge_variant": "teal",
            "image_url": "/shopping/travel-essentials.png", "x_coord": 610.0, "y_coord": 450.0
        },

        # --- Lounges ---
        {
            "id": "poi_l1", "name": "Encalm Lounge (T3)", "category": "lounges", "sub_category": "t3,international,24hr,premium",
            "description": "Premium lounge offering buffet dining, high-speed Wi-Fi, shower suites and quiet work pods.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Near Gate 15",
            "distance_m": 120, "image_url": "/lounges/encalm-lounge.png", "badge_label": "Premium", "badge_variant": "purple",
            "x_coord": 600.0, "y_coord": 300.0
        },
        {
            "id": "poi_l2", "name": "Plaza Premium Lounge", "category": "lounges", "sub_category": "t3,international,24hr,business",
            "description": "International departure lounge with chef stations, barista coffee, nap rooms and shower facilities.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "International Departures Pier",
            "distance_m": 180, "image_url": "/lounges/plaza-premium.png", "badge_label": "International", "badge_variant": "teal",
            "x_coord": 620.0, "y_coord": 270.0
        },
        {
            "id": "poi_l3", "name": "Air India Maharaja Lounge", "category": "lounges", "sub_category": "t3,domestic,premium",
            "description": "Dedicated lounge for Business & First Class passengers with full bar and hot meals.",
            "operating_hours": "04:30 AM – 11:30 PM", "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Near Gate 28",
            "distance_m": 230, "image_url": "/lounges/air-india-lounge.png", "badge_label": "Star Alliance", "badge_variant": "amber",
            "x_coord": 590.0, "y_coord": 260.0
        },

        # --- Services ---
        {
            "id": "poi_srv1", "name": "Central Airport Information Desk", "category": "services", "sub_category": "assistance",
            "description": "24/7 passenger assistance, flight inquiry, wheelchair requests and airport guidance.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Main Atrium",
            "distance_m": 45, "badge_label": "Info", "badge_variant": "teal",
            "image_url": "/services/info-desk.png", "x_coord": 500.0, "y_coord": 350.0
        },
        {
            "id": "poi_srv2", "name": "Thomas Cook Currency Exchange & ATM", "category": "services", "sub_category": "financial",
            "description": "Foreign currency exchange for 26+ currencies, multi-currency cards and multi-bank ATMs.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 16",
            "distance_m": 85, "badge_label": "Forex", "badge_variant": "amber",
            "image_url": "/services/forex-atm.png", "x_coord": 530.0, "y_coord": 360.0
        },
        {
            "id": "poi_srv3", "name": "Left Luggage & Cloak Room", "category": "services", "sub_category": "baggage",
            "description": "Secure short-term and long-term baggage storage, luggage wrapping and strapping.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Ground Level", "gate": "Near Arrival Gate 4",
            "distance_m": 210, "image_url": "/services/left-luggage.png", "x_coord": 480.0, "y_coord": 400.0
        },
        {
            "id": "poi_srv4", "name": "Airtel & Jio International SIM Counter", "category": "services", "sub_category": "telecom",
            "description": "Instant tourist SIM card activation, international roaming packs and 5G data plans.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Arrivals Hall", "gate": "Exit Gate 6",
            "distance_m": 160, "image_url": "/services/sim-counter.png", "x_coord": 510.0, "y_coord": 390.0
        },

        # --- Amenities ---
        {
            "id": "poi_am1", "name": "Executive Restroom (Male & Female)", "category": "amenities", "sub_category": "restroom",
            "description": "Touchless, hygienic restrooms equipped with wheelchair accessible cubicles.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Opposite Gate 21",
            "distance_m": 50, "badge_label": "Free", "badge_variant": "teal",
            "image_url": "/amenities/restroom.png", "x_coord": 540.0, "y_coord": 340.0
        },
        {
            "id": "poi_am2", "name": "RO Purified Drinking Water Station", "category": "amenities", "sub_category": "water",
            "description": "Free temperature-controlled RO filtered drinking water and bottle refill station.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 17",
            "distance_m": 60, "badge_label": "Free", "badge_variant": "teal",
            "image_url": "/amenities/water-station.png", "x_coord": 560.0, "y_coord": 350.0
        },
        {
            "id": "poi_am3", "name": "Multi-Faith Prayer Room", "category": "amenities", "sub_category": "prayer",
            "description": "Quiet prayer and meditation space with ablution facilities for all travelers.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Near Gate 34",
            "distance_m": 220, "image_url": "/amenities/prayer-room.png", "x_coord": 570.0, "y_coord": 250.0
        },
        {
            "id": "poi_am4", "name": "Baby Care & Nursing Room", "category": "amenities", "sub_category": "babycare",
            "description": "Private, sanitized nursing cubicles, baby diaper changing stations and hot water kettle.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Near Gate 20",
            "distance_m": 110, "badge_label": "Family", "badge_variant": "purple",
            "image_url": "/amenities/baby-care.png", "x_coord": 550.0, "y_coord": 330.0
        },
        {
            "id": "poi_am5", "name": "Device Fast Charging Station", "category": "amenities", "sub_category": "charging",
            "description": "High-speed USB-A, USB-C (65W PD) and universal AC power outlets for smartphones and laptops.",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 1", "gate": "Gate 15 Waiting Area",
            "distance_m": 75, "badge_label": "Free", "badge_variant": "teal",
            "image_url": "/amenities/charging-station.png", "x_coord": 580.0, "y_coord": 360.0
        },

        # --- Boarding Gates ---
        {
            "id": "poi_gate_b12", "name": "Boarding Gate B12", "category": "gates", "sub_category": "t3,domestic",
            "description": "Departure Gate B12 — Boarding Concourse Level 2",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Gate B12",
            "distance_m": 95, "image_url": "/gates/gate-b12.png", "x_coord": 320.0, "y_coord": 250.0
        },
        {
            "id": "poi_gate_b24", "name": "Boarding Gate B24", "category": "gates", "sub_category": "t3,domestic",
            "description": "Departure Gate B24 — Domestic Concourse Pier 2",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Gate B24",
            "distance_m": 140, "image_url": "/gates/gate-b24.png", "x_coord": 360.0, "y_coord": 280.0
        },
        {
            "id": "poi_gate_c32", "name": "Boarding Gate C32", "category": "gates", "sub_category": "t3,international",
            "description": "Departure Gate C32 — International Concourse Pier 3",
            "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "Level 2", "gate": "Gate C32",
            "distance_m": 290, "image_url": "/gates/gate-c32.png", "x_coord": 410.0, "y_coord": 310.0
        }
    ]
