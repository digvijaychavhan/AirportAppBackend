"""
Database Migration & Seed Script
Populates SQLite / PostgreSQL database with realistic Airport domain objects
"""

from datetime import datetime, timedelta
from database import engine, Base, SessionLocal
from models import Airline, Flight, Kiosk, MapFloor, MapNode, MapEdge, Poi, Operator, WayfindingCategory

def seed_database(force: bool = False):
    print("Ensuring database tables exist...")
    if force:
        print("Force option set: Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if not force:
            existing_airline = db.query(Airline).first()
            existing_cat = db.query(WayfindingCategory).first()
            if existing_airline and existing_cat:
                print("Database already initialized and seeded. Skipping seed process.")
                return

        print("Seeding Airlines...")
        airlines = [
            Airline(code="6E", name="IndiGo", logo_url="/logos/indigo.png", flight_type="DOMESTIC"),
            Airline(code="AI", name="Air India", logo_url="/logos/airindia.png", flight_type="INTERNATIONAL"),
            Airline(code="UK", name="Vistara", logo_url="/logos/vistara.png", flight_type="DOMESTIC"),
            Airline(code="SG", name="SpiceJet", logo_url="/logos/spicejet.png", flight_type="DOMESTIC"),
            Airline(code="EK", name="Emirates", logo_url="/logos/emirates.png", flight_type="INTERNATIONAL"),
        ]
        db.add_all(airlines)
        db.commit()

        print("Seeding Flights...")
        now = datetime.utcnow()
        flights = [
            Flight(
                id="fl_6e203",
                flight_number="6E 203",
                airline_code="6E",
                origin_iata="DEL",
                destination_iata="MAA",
                destination_name="Chennai (MAA)",
                scheduled_departure=now + timedelta(hours=2),
                estimated_departure=now + timedelta(hours=2),
                terminal="T3",
                gate="Gate B14",
                checkin_counters="45 – 52",
                baggage_belt="Carousel 4",
                status="ON_TIME"
            ),
            Flight(
                id="fl_ai101",
                flight_number="AI 101",
                airline_code="AI",
                origin_iata="DEL",
                destination_iata="LHR",
                destination_name="London Heathrow (LHR)",
                scheduled_departure=now + timedelta(hours=1, minutes=15),
                estimated_departure=now + timedelta(hours=1, minutes=15),
                terminal="T3",
                gate="Gate A08",
                checkin_counters="12 – 24",
                baggage_belt="Carousel 9",
                status="BOARDING"
            ),
            Flight(
                id="fl_uk815",
                flight_number="UK 815",
                airline_code="UK",
                origin_iata="DEL",
                destination_iata="BOM",
                destination_name="Mumbai (BOM)",
                scheduled_departure=now + timedelta(hours=3, minutes=30),
                estimated_departure=now + timedelta(hours=4, minutes=10),
                terminal="T3",
                gate="Gate B16",
                checkin_counters="30 – 40",
                baggage_belt="Carousel 2",
                status="DELAYED"
            ),
            Flight(
                id="fl_sg402",
                flight_number="SG 402",
                airline_code="SG",
                origin_iata="DEL",
                destination_iata="BLR",
                destination_name="Bengaluru (BLR)",
                scheduled_departure=now + timedelta(hours=4),
                estimated_departure=now + timedelta(hours=4),
                terminal="T1",
                gate="Gate A04",
                checkin_counters="05 – 09",
                baggage_belt="Carousel 1",
                status="ON_TIME"
            ),
            Flight(
                id="fl_ek511",
                flight_number="EK 511",
                airline_code="EK",
                origin_iata="DEL",
                destination_iata="DXB",
                destination_name="Dubai (DXB)",
                scheduled_departure=now + timedelta(hours=2, minutes=45),
                estimated_departure=now + timedelta(hours=2, minutes=45),
                terminal="T3",
                gate="Gate A17",
                checkin_counters="01 – 08",
                baggage_belt="Carousel 5",
                status="GATE_CHANGE"
            ),
        ]
        db.add_all(flights)
        db.commit()

        print("Seeding MapFloors...")
        floors = [
            MapFloor(id="floor-l1", building="Main Terminal", floor_level=1, svg_asset_url="http://localhost:5000/assets/map_floor_l1.svg"),
            MapFloor(id="floor-l2", building="Main Terminal", floor_level=2, svg_asset_url="http://localhost:5000/assets/map_floor_l2.svg"),
        ]
        db.add_all(floors)
        db.commit()

        print("Seeding MapNodes...")
        nodes = [
            # Floor L1 nodes
            MapNode(id="node-l1-01", floor_id="floor-l1", x_coord=100.0, y_coord=200.0, zone_name="Arrivals Entrance & Kiosk Area"),
            MapNode(id="node-l1-02", floor_id="floor-l1", x_coord=250.0, y_coord=200.0, zone_name="Central Concourse L1"),
            MapNode(id="node-l1-03", floor_id="floor-l1", x_coord=400.0, y_coord=200.0, zone_name="Elevator Hub L1", is_vertical_connector=True, connector_type="elevator"),
            MapNode(id="node-l1-04", floor_id="floor-l1", x_coord=550.0, y_coord=200.0, zone_name="Baggage Reclaim Belts 1-4"),
            MapNode(id="node-l1-05", floor_id="floor-l1", x_coord=700.0, y_coord=200.0, zone_name="Food Court & Cafe L1"),
            MapNode(id="node-l1-06", floor_id="floor-l1", x_coord=400.0, y_coord=350.0, zone_name="Escalator Hub L1", is_vertical_connector=True, connector_type="escalator"),

            # Floor L2 nodes
            MapNode(id="node-l2-01", floor_id="floor-l2", x_coord=100.0, y_coord=200.0, zone_name="Security Checkpoint L2"),
            MapNode(id="node-l2-02", floor_id="floor-l2", x_coord=250.0, y_coord=200.0, zone_name="Duty Free Concourse L2"),
            MapNode(id="node-l2-03", floor_id="floor-l2", x_coord=400.0, y_coord=200.0, zone_name="Elevator Hub L2", is_vertical_connector=True, connector_type="elevator"),
            MapNode(id="node-l2-04", floor_id="floor-l2", x_coord=600.0, y_coord=150.0, zone_name="Boarding Gates 1-10"),
            MapNode(id="node-l2-05", floor_id="floor-l2", x_coord=600.0, y_coord=300.0, zone_name="Boarding Gates 11-25"),
            MapNode(id="node-l2-06", floor_id="floor-l2", x_coord=400.0, y_coord=350.0, zone_name="Escalator Hub L2", is_vertical_connector=True, connector_type="escalator"),
        ]
        db.add_all(nodes)
        db.commit()

        print("Seeding MapEdges...")
        edges = [
            # Floor L1 edges
            MapEdge(id="edge-l1-1-2", source_node_id="node-l1-01", target_node_id="node-l1-02", distance_meters=15.0),
            MapEdge(id="edge-l1-2-3", source_node_id="node-l1-02", target_node_id="node-l1-03", distance_meters=20.0),
            MapEdge(id="edge-l1-3-4", source_node_id="node-l1-03", target_node_id="node-l1-04", distance_meters=25.0),
            MapEdge(id="edge-l1-4-5", source_node_id="node-l1-04", target_node_id="node-l1-05", distance_meters=30.0),
            MapEdge(id="edge-l1-2-6", source_node_id="node-l1-02", target_node_id="node-l1-06", distance_meters=18.0),

            # Floor L2 edges
            MapEdge(id="edge-l2-1-2", source_node_id="node-l2-01", target_node_id="node-l2-02", distance_meters=15.0),
            MapEdge(id="edge-l2-2-3", source_node_id="node-l2-02", target_node_id="node-l2-03", distance_meters=20.0),
            MapEdge(id="edge-l2-3-4", source_node_id="node-l2-03", target_node_id="node-l2-04", distance_meters=35.0),
            MapEdge(id="edge-l2-3-5", source_node_id="node-l2-03", target_node_id="node-l2-05", distance_meters=30.0),
            MapEdge(id="edge-l2-2-6", source_node_id="node-l2-02", target_node_id="node-l2-06", distance_meters=18.0),

            # Inter-floor vertical connectors
            MapEdge(id="edge-vert-elev", source_node_id="node-l1-03", target_node_id="node-l2-03", distance_meters=5.0, is_accessible_elevator=True, is_escalator=False),
            MapEdge(id="edge-vert-esc", source_node_id="node-l1-06", target_node_id="node-l2-06", distance_meters=8.0, is_accessible_elevator=False, is_escalator=True),
        ]
        db.add_all(edges)
        db.commit()

        print("Seeding POIs...")
        pois = [
            # Restaurants & Dining
            Poi(id="r1", name="Third Wave Coffee", category="Dining", sub_category="cafe", description="Specialty coffee, pastries, sandwiches & more", terminal="T3 Departure", floor_name="Level 2", gate="Near Gate 24", node_id="node-l2-02", floor_id="floor-l2", operating_hours="6:00 AM – 11:00 PM", distance_m=120, image_url="/restaurants/third-wave-coffee.png", rating=4.8),
            Poi(id="r2", name="McDonald's", category="Dining", sub_category="fastfood", description="Burgers, fries, beverages and more", terminal="T3 Departure", floor_name="Food Court", gate="", node_id="node-l1-05", floor_id="floor-l1", operating_hours="24 Hours", distance_m=150, image_url="/restaurants/mcdonalds.png", rating=4.6),
            Poi(id="r3", name="Bikanervala", category="Dining", sub_category="indian", description="North Indian snacks, meals & sweets", terminal="T3 Departure", floor_name="", gate="Near Gate 19", node_id="node-l2-02", floor_id="floor-l2", operating_hours="6:00 AM – 11:00 PM", distance_m=180, image_url="/restaurants/bikanervala.png", rating=4.7),
            Poi(id="r4", name="Subway", category="Dining", sub_category="fastfood", description="Sandwiches, salads & wraps", terminal="T3 Departure", floor_name="Food Court", gate="", node_id="node-l1-05", floor_id="floor-l1", operating_hours="6:00 AM – 12:00 AM", distance_m=210, image_url="/restaurants/subway.png", rating=4.4),
            Poi(id="r5", name="Sichuan House", category="Dining", sub_category="asian", description="Chinese cuisine, noodles & rice", terminal="T3 Departure", floor_name="", gate="Near Gate 32", node_id="node-l2-05", floor_id="floor-l2", operating_hours="11:00 AM – 11:00 PM", distance_m=260, image_url="/restaurants/sichuan-house.png", rating=4.5),

            # Lounges
            Poi(id="l1", name="Encalm Lounge", category="Lounge", sub_category="t3,international,24hr,premium", description="Premium lounge offering gourmet dining, Wi-Fi, shower facilities and business workstations.", terminal="Terminal 3", gate="Near Gate 15", node_id="node-l2-02", floor_id="floor-l2", operating_hours="24 Hours", distance_m=120, image_url="/lounges/encalm-lounge.png", badge_label="Premium", badge_variant="purple", rating=4.9),
            Poi(id="l2", name="Plaza Premium Lounge", category="Lounge", sub_category="t3,international,24hr,business", description="International lounge with buffet, shower rooms and dedicated business zone.", terminal="Terminal 3", gate="International Departures", node_id="node-l2-02", floor_id="floor-l2", operating_hours="24 Hours", distance_m=180, image_url="/lounges/plaza-premium.png", badge_label="International", badge_variant="teal", rating=4.7),
            Poi(id="l3", name="Air India Maharaja Lounge", category="Lounge", sub_category="t3,international,24hr,business", description="Exclusive lounge for Air India Business and First Class passengers.", terminal="Terminal 3", gate="Near Gate 22", node_id="node-l2-02", floor_id="floor-l2", operating_hours="24 Hours", distance_m=210, image_url="/lounges/maharaja-lounge.png", badge_label="Business Class", badge_variant="amber", rating=4.8),
            Poi(id="l4", name="Travel Club Lounge", category="Lounge", sub_category="t2,domestic", description="Comfortable lounge with refreshments, Wi-Fi and charging stations.", terminal="Terminal 2", gate="Near Security", node_id="node-l1-02", floor_id="floor-l1", operating_hours="05:00 AM – 11:00 PM", distance_m=260, image_url="/lounges/travel-club.png", badge_label="Domestic", badge_variant="green", rating=4.4),
            Poi(id="l5", name="Premium Lounge", category="Lounge", sub_category="t1,premium,24hr", description="Quiet premium lounge offering complimentary meals and beverages.", terminal="Terminal 1", gate="Near Gate 5", node_id="node-l1-01", floor_id="floor-l1", operating_hours="24 Hours", distance_m=300, image_url="/lounges/premium-lounge.png", badge_label="VIP", badge_variant="red", rating=4.6),

            # Stores & Retail
            Poi(id="s1", name="Duty Free", category="Retail", sub_category="dutyfree", description="Luxury perfumes, cosmetics, chocolates, liquor and travel exclusives.", terminal="Terminal 3", gate="Near Gate 18", node_id="node-l2-02", floor_id="floor-l2", operating_hours="24 Hours", distance_m=110, image_url="/shopping/duty-free.png", rating=4.8),
            Poi(id="s2", name="Imagine Store", category="Retail", sub_category="electronics", description="Apple products, accessories and premium electronics.", terminal="Terminal 3", gate="Near Gate 22", node_id="node-l2-02", floor_id="floor-l2", operating_hours="06:00 AM – 11:00 PM", distance_m=150, image_url="/shopping/imagine-store.png", rating=4.7),
            Poi(id="s3", name="Hidesign", category="Retail", sub_category="fashion", description="Leather bags, wallets, backpacks and travel accessories.", terminal="Terminal 3", gate="Near Gate 30", node_id="node-l2-05", floor_id="floor-l2", operating_hours="08:00 AM – 10:00 PM", distance_m=190, image_url="/shopping/hidesign.png", rating=4.6),
            Poi(id="s4", name="Relay Books", category="Retail", sub_category="books", description="Books, magazines, snacks and travel accessories.", terminal="Terminal 3", gate="Near Gate 11", node_id="node-l2-04", floor_id="floor-l2", operating_hours="05:00 AM – 11:00 PM", distance_m=220, image_url="/shopping/relay-books.png", rating=4.5),
            Poi(id="s5", name="Travel Essentials", category="Retail", sub_category="convenience", description="Everything you need for your journey.", terminal="Terminal 3", gate="Near Security Exit", node_id="node-l1-02", floor_id="floor-l1", operating_hours="24 Hours", distance_m=250, image_url="/shopping/travel-essentials.png", rating=4.3),

            # Gates, Restrooms, Services & Information
            Poi(id="poi-04", name="Gate 14 Boarding Area", category="Gate", sub_category="gates", node_id="node-l2-05", floor_id="floor-l2", operating_hours="24/7", rating=4.5),
            Poi(id="poi-05", name="ADA Wheelchair Accessible Restroom", category="Restroom", sub_category="restroom", node_id="node-l1-02", floor_id="floor-l1", operating_hours="24/7", rating=4.9),
            Poi(id="poi-06", name="Baggage Reclaim Belt 04", category="Services", sub_category="services", node_id="node-l1-04", floor_id="floor-l1", operating_hours="24/7", rating=4.2),
            Poi(id="poi-07", name="Airport Information Desk", category="Information", sub_category="info", node_id="node-l1-01", floor_id="floor-l1", operating_hours="24/7", rating=4.8),
        ]
        db.add_all(pois)
        db.commit()

        print("Seeding Kiosks...")
        kiosks = [
            Kiosk(id="T3-L1-K04", code="T3-L1-K04", terminal="Terminal 3", floor_id="floor-l1", current_node_id="node-l1-01", is_accessible_ada=True, status="active"),
            Kiosk(id="T2-A87", code="T2-A87", terminal="Terminal 2", floor_id="floor-l1", current_node_id="node-l1-02", is_accessible_ada=True, status="active"),
            Kiosk(id="T1-D12", code="T1-D12", terminal="Terminal 1", floor_id="floor-l2", current_node_id="node-l2-01", is_accessible_ada=True, status="active"),
        ]
        db.add_all(kiosks)
        db.commit()

        print("Seeding Operators...")
        operators = [
            Operator(id="op_101", employee_code="EMP-9021", name="Priya Sharma", role="CUSTOMER_SUPPORT_EXECUTIVE", status="ONLINE", supported_languages="EN,HI,TA"),
            Operator(id="op_102", employee_code="EMP-9022", name="Rahul Verma", role="ACCESSIBILITY_SPECIALIST", status="ONLINE", supported_languages="EN,HI,MR"),
            Operator(id="op_103", employee_code="EMP-9023", name="Ananya Patel", role="CUSTOMER_SUPPORT_EXECUTIVE", status="ONLINE", supported_languages="EN,GU,HI"),
        ]
        db.add_all(operators)
        db.commit()

        print("Seeding WayfindingCategories...")
        wayfinding_categories = [
            WayfindingCategory(
                id="shopping",
                title="Shopping",
                description="Explore shops and\nretail stores",
                photo_url="/findway-shopping.png",
                icon="shopping_bag",
                icon_color="#2563EB",
                icon_bg="#DBEAFE",
                route="/wayfinding/shopping"
            ),
            WayfindingCategory(
                id="dining",
                title="Eat & Dine",
                description="Restaurants, cafes\nand fast food",
                photo_url="/findway-dining.png",
                icon="restaurant",
                icon_color="#D97706",
                icon_bg="#FEF3C7",
                route="/eat-dine"
            ),
            WayfindingCategory(
                id="services",
                title="Services",
                description="Assistance, counters\nand other services",
                photo_url="/findway-services.png",
                icon="support_agent",
                icon_color="#7C3AED",
                icon_bg="#EDE9FE",
                route="/wayfinding/services"
            ),
            WayfindingCategory(
                id="gates",
                title="Boarding Gates",
                description="Find your boarding gates\nand directions",
                photo_url="/findway-gates.png",
                icon="flight_takeoff",
                icon_color="#059669",
                icon_bg="#D1FAE5",
                route="/wayfinding/gates"
            ),
            WayfindingCategory(
                id="lounges",
                title="Lounges",
                description="Airport lounges and\nrelaxation areas",
                photo_url="/findway-lounge.png",
                icon="weekend",
                icon_color="#DB2777",
                icon_bg="#FCE7F3",
                route="/wayfinding/lounges"
            ),
            WayfindingCategory(
                id="amenities",
                title="Airport Amenities",
                description="Facilities like restrooms,\nprayer rooms and more",
                photo_url="/findway-amenities.png",
                icon="wc",
                icon_color="#0891B2",
                icon_bg="#CFFAFE",
                route="/wayfinding/amenities"
            ),
        ]
        db.add_all(wayfinding_categories)
        db.commit()

        print("Database successfully seeded!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    force_seed = "--force" in sys.argv or "-f" in sys.argv
    seed_database(force=force_seed)
