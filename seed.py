"""
Database Migration & Seed Script
Populates SQLite / PostgreSQL database with realistic Airport domain objects
"""

from datetime import datetime, timedelta
from database import engine, Base, SessionLocal
from models import Airline, Flight, Kiosk, MapFloor, MapNode, MapEdge, Poi, Operator

def seed_database():
    print("Creating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
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
            Poi(id="poi-01", name="Delhi Chai Co & Bakery", category="Dining", node_id="node-l1-05", floor_id="floor-l1", operating_hours="24/7", dietary_tags="Vegetarian, Jain Options, Vegan", rating=4.8),
            Poi(id="poi-02", name="Plaza Premium Lounge", category="Lounge", node_id="node-l2-02", floor_id="floor-l2", operating_hours="24/7", dietary_tags="Multi-Cuisine Buffet", rating=4.7),
            Poi(id="poi-03", name="Duty Free World", category="Retail", node_id="node-l2-02", floor_id="floor-l2", operating_hours="24/7", rating=4.6),
            Poi(id="poi-04", name="Gate 14 Boarding Area", category="Gate", node_id="node-l2-05", floor_id="floor-l2", operating_hours="24/7", rating=4.5),
            Poi(id="poi-05", name="ADA Wheelchair Accessible Restroom", category="Restroom", node_id="node-l1-02", floor_id="floor-l1", operating_hours="24/7", rating=4.9),
            Poi(id="poi-06", name="Baggage Reclaim Belt 04", category="Services", node_id="node-l1-04", floor_id="floor-l1", operating_hours="24/7", rating=4.2),
            Poi(id="poi-07", name="Airport Information Desk", category="Information", node_id="node-l1-01", floor_id="floor-l1", operating_hours="24/7", rating=4.8),
            Poi(id="poi-08", name="Starbucks Coffee", category="Dining", node_id="node-l2-01", floor_id="floor-l2", operating_hours="05:00 - 23:00", dietary_tags="Oat Milk, Gluten-Free Snacks", rating=4.5),
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

        print("Database successfully seeded!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
